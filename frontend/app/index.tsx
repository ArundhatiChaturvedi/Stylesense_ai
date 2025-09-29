import React, { useState, useRef } from 'react';
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  Alert,
  ImageBackground,
  Image,
  KeyboardAvoidingView,
  TouchableWithoutFeedback,
  Keyboard,
  Platform,
  StyleSheet
} from 'react-native';
import { useRouter } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome5, MaterialCommunityIcons, Ionicons } from '@expo/vector-icons';

import { styleSenseAPI } from './services/api';
import { useUser } from '../contexts/UserContext';
import { UploadProgressView } from '../components/uploadProgressView';
import { simulateDelay } from '../utils/helpers';

const splashBg = require('../assets/images/splash_bg.png');
const profilePic = require('../assets/images/profile_pic.png');

export default function HomeScreen() {
  const { userId, userStatus, refreshUserStatus } = useUser();
  const [inputText, setInputText] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatusText, setUploadStatusText] = useState('Initializing upload...');
  
  const userName = 'Prism'; 
  const router = useRouter(); 
  const animatedValue = useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(animatedValue, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: false,
        }),
        Animated.timing(animatedValue, {
          toValue: 0,
          duration: 2000,
          useNativeDriver: false,
        }),
      ])
    );
    animation.start();
  }, []);

  const start = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [{ x: 0, y: 0 }, { x: 1, y: 1 }],
  });

  const end = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: [{ x: 1, y: 1 }, { x: 0, y: 0 }],
  });

  const AnimatedLinearGradient = Animated.createAnimatedComponent(LinearGradient);

  const handleAskAI = async () => {
    if (!inputText.trim()) {
      Alert.alert('Error', 'Please enter your style question');
      return;
    }

    if (!userStatus?.user_exists) {
      Alert.alert(
        'Setup Required', 
        'Please upload your wardrobe photos first using the "Upload Outfit" button!',
        [{ text: 'OK', style: 'default' }]
      );
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress(0);
      setUploadStatusText('Getting your location...');

      let currentLocation = 'Mumbai';
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === 'granted') {
          const location = await Location.getCurrentPositionAsync({});
          const [address] = await Location.reverseGeocodeAsync({
            latitude: location.coords.latitude,
            longitude: location.coords.longitude,
          });
          currentLocation = address.city || address.region || 'Mumbai';
        }
      } catch (locationError) {
        console.log('Location error:', locationError);
      }

      setUploadProgress(20);
      setUploadStatusText('Analyzing your style request...');

      const recommendation = await styleSenseAPI.getStyleRecommendation({
        user_id: userId,
        user_prompt: inputText,
        current_location: currentLocation
      });

      setUploadProgress(80);
      setUploadStatusText('Preparing your style advice...');

      await simulateDelay(1000);

      setUploadProgress(100);
      setUploadStatusText('Complete! Redirecting...');

      await simulateDelay(500);

      router.push({
        pathname: "/screens/recommend",
        params: {
          recommendation: JSON.stringify(recommendation),
          userPrompt: inputText
        }
      });

    } catch (error) {
      console.error('AI recommendation error:', error);
      Alert.alert(
        'Error', 
        error instanceof Error ? error.message : 'Failed to get style recommendation'
      );
    } finally {
      setIsUploading(false);
      setInputText('');
    }
  };

  const uploadImageToBackend = async (imageUri: string, base64Data?: string) => {
    try {
      let imageBase64 = base64Data;
      
      if (!imageBase64) {
        const response = await fetch(imageUri);
        const blob = await response.blob();
        const reader = new FileReader();
        
        return new Promise((resolve, reject) => {
          reader.onloadend = async () => {
            try {
              const base64String = (reader.result as string).split(',')[1];
              const uploadResponse = await styleSenseAPI.uploadWardrobeBase64(userId, base64String);
              resolve(uploadResponse);
            } catch (error) {
              reject(error);
            }
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        });
      } else {
        return await styleSenseAPI.uploadWardrobeBase64(userId, imageBase64);
      }
    } catch (error) {
      console.error('Upload to backend failed:', error);
      throw error;
    }
  };

  const simulateProcessingWithRealUpload = async (selectedImages: any[]) => {
    const totalSteps = 3 + selectedImages.length;
    let currentStep = 0;

    setUploadStatusText('Preparing to upload...');
    setUploadProgress(Math.floor((currentStep / totalSteps) * 100));
    await simulateDelay(800);

    currentStep++;
    setUploadStatusText('Initializing AI analysis...');
    setUploadProgress(Math.floor((currentStep / totalSteps) * 100));
    await simulateDelay(1000);

    let uploadedCount = 0;
    for (let i = 0; i < selectedImages.length; i++) {
      const image = selectedImages[i];
      currentStep++;
      
      setUploadStatusText(`Analyzing outfit ${i + 1} of ${selectedImages.length}...`);
      setUploadProgress(Math.floor((currentStep / totalSteps) * 100));

      try {
        await uploadImageToBackend(image.uri, image.base64);
        uploadedCount++;
        await simulateDelay(600);
      } catch (error) {
        console.error(`Upload error for image ${i + 1}:`, error);
      }
    }

    currentStep++;
    setUploadStatusText('Processing your wardrobe...');
    setUploadProgress(Math.floor((currentStep / totalSteps) * 100));
    await simulateDelay(1500);

    currentStep++;
    setUploadStatusText('Complete! Redirecting...');
    setUploadProgress(100);
    await simulateDelay(500);

    await refreshUserStatus();

    Alert.alert(
      'Upload Complete!', 
      `Successfully uploaded ${uploadedCount} out of ${selectedImages.length} images to your wardrobe.`,
      [
        { text: 'OK', onPress: () => {
          setIsUploading(false);
          router.push("/screens/model");
        }}
      ]
    );
  };

  const handleUploadNewOutfit = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (permissionResult.granted === false) {
      Alert.alert('Permission Denied', 'Permission to access the photo gallery is required to upload outfits.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultipleSelection: true,
      selectionLimit: 5,
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      setIsUploading(true);
      setUploadProgress(0);

      try {
        await simulateProcessingWithRealUpload(result.assets);
      } catch (error) {
        console.error('Upload process failed:', error);
        Alert.alert('Upload Failed', 'Some images could not be uploaded. Please try again.');
        setIsUploading(false);
      }
    }
  };

  const handleLoadOrderHistory = async () => {
    try {
      setIsUploading(true);
      setUploadStatusText('Loading your purchase history...');
      setUploadProgress(50);

      const response = await styleSenseAPI.loadOrderHistory(userId);
      
      setUploadProgress(100);
      await simulateDelay(500);

      if (response.success) {
        Alert.alert('Success', response.message);
        await refreshUserStatus();
      } else {
        Alert.alert('Info', response.message);
      }
    } catch (error) {
      console.error('Load order history error:', error);
      Alert.alert('Error', error instanceof Error ? error.message : 'Failed to load order history');
    } finally {
      setIsUploading(false);
    }
  };

  const handleProfilePress = () => {
    router.push("/screens/profile");
  };

  const handleMyCloset = () => {
    router.push("/screens/model");
  };

  return (
    <ImageBackground source={splashBg} style={styles.background}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <TouchableWithoutFeedback onPress={Keyboard.dismiss} disabled={isUploading}>
          <View style={styles.scrollContentContainer}>
            <View style={styles.topRightProfile}>
              <TouchableOpacity onPress={handleProfilePress} style={styles.profileContainer}>
                <View style={styles.profilePicBorder}>
                  <Image source={profilePic} style={styles.profilePic} />
                </View>
              </TouchableOpacity>
            </View>

            {userStatus && (
              <View style={styles.statusIndicator}>
                <Text style={styles.statusText}>
                  {userStatus.user_exists 
                    ? `✅ ${userStatus.total_items} items in wardrobe`
                    : '⚠ Upload outfits to get started'
                  }
                </Text>
              </View>
            )}

            <View style={styles.contentBox}>
              {isUploading ? (
                <UploadProgressView progress={uploadProgress} statusText={uploadStatusText} />
              ) : (
                <>
                  <Text style={styles.greetingText}>
                    Hey {userName}, ask me anything about your style!
                  </Text>

                  <View style={styles.aiInputWrapper}>
                    <TextInput
                      style={styles.aiInputField}
                      placeholder="Looking for inspiration? Try asking me.."
                      placeholderTextColor="#B0B0B0"
                      value={inputText}
                      onChangeText={setInputText}
                      multiline={true}
                      numberOfLines={4}
                      textAlignVertical="top"
                    />
                    <TouchableOpacity style={styles.sendButton} onPress={handleAskAI}>
                      <Ionicons name="send" size={18} color="#d07988ff" />
                    </TouchableOpacity>
                  </View>

                  <View style={styles.buttonsRow}>
                    <TouchableOpacity onPress={handleUploadNewOutfit} style={{ flex: 1 }}>
                      <AnimatedLinearGradient
                        colors={['#e68998', '#ffb6c1', '#e68998']}
                        start={start}
                        end={end}
                        style={styles.uploadButton}
                      >
                        <FontAwesome5 name="camera" size={20} color="#FFF" style={styles.iconStyle} />
                        <Text style={[styles.buttonText, { color: '#FFF' }]}>Upload Outfit</Text>
                      </AnimatedLinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.myClosetButton}
                      onPress={handleMyCloset}
                    >
                      <MaterialCommunityIcons name="hanger" size={22} color="#e68998" style={styles.iconStyle} />
                      <Text style={styles.buttonText}>My Closet</Text>
                    </TouchableOpacity>
                  </View>

                  {!userStatus?.user_exists && (
                    <TouchableOpacity
                      style={styles.orderHistoryButton}
                      onPress={handleLoadOrderHistory}
                    >
                      <Text style={styles.orderHistoryButtonText}>
                        Or Load Sample Order History
                      </Text>
                    </TouchableOpacity>
                  )}
                </>
              )}
            </View>

            <Text style={styles.samsungPrismText}>SAMSUNG PRISM</Text>
          </View>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    resizeMode: 'cover',
    justifyContent: 'center',
    alignItems: 'center',
  },
  keyboardAvoidingContainer: {
    flex: 1,
    width: '100%',
  },
  scrollContentContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  topRightProfile: {
    position: 'absolute',
    top: 70, 
    right: 20,
    alignItems: 'center',
  },
  profileContainer: {
    alignItems: 'center',
  },
  profilePicBorder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 1,
    borderColor: '#bd5afaff',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFF',
  },
  profilePic: {
    width: 70,
    height: 70,
    borderRadius: 35,
    resizeMode: 'cover',
  },
  statusIndicator: {
    position: 'absolute',
    top: 160,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  contentBox: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 25,
    padding: 25,
    width: '90%',
    maxWidth: 400, 
    alignItems: 'center',
    elevation: 5,
    marginBottom: 40,
    marginTop: 150,
    minHeight: 250,
    justifyContent: 'center', 
  },
  greetingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  aiInputWrapper: {
    backgroundColor: '#f0f0f0',
    borderRadius: 15,
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginBottom: 25,
    width: '100%',
    minHeight: 100,
    position: 'relative',
  },
  aiInputField: {
    flex: 1,
    minHeight: 80,
    fontSize: 16,
    color: '#333',
    textAlignVertical: 'top',
  },
  sendButton: {
    position: 'absolute',
    bottom: 12,
    right: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 20,
    padding: 8,
    elevation: 3,
  },
  buttonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    gap: 10,
    marginBottom: 10, 
  },
  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 20,
    paddingVertical: 12,
    paddingHorizontal: 15,
    flex: 1,
    justifyContent: 'center',
  },
  myClosetButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF0F5',
    borderRadius: 20,
    paddingVertical: 12,
    paddingHorizontal: 15,
    flex: 1,
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#eeb3b3',
  },
  iconStyle: { 
    marginRight: 6,
  },
  buttonText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333', 
  },
  orderHistoryButton: {
    marginTop: 10,
    paddingVertical: 10,
  },
  orderHistoryButtonText: {
    fontSize: 14,
    color: '#007bff',
    textDecorationLine: 'underline',
  },
  samsungPrismText: {
    position: 'absolute', 
    bottom: 20,
    marginBottom: 10,
    fontSize: 18.5,
    color: '#ffffff',
    letterSpacing: 1,
  },
});