import React, { useState, useRef, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ImageBackground,
  Image,
  KeyboardAvoidingView,
  Platform,
  TouchableWithoutFeedback,
  Keyboard,
  Animated,
  ActivityIndicator,
  Alert, 
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome5, Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router'; 
import * as ImagePicker from 'expo-image-picker'; 

const AnimatedLinearGradient = Animated.createAnimatedComponent(LinearGradient);

const profilePic = require("../assets/images/profile_pic.png"); 
const splashBg = require("../assets/images/splash_bg.png"); 
interface UploadProgressViewProps {
  progress: number; 
  statusText: string;
}

const UploadProgressView: React.FC<UploadProgressViewProps> = ({ progress, statusText }) => {
  const animatedWidth = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(animatedWidth, {
      toValue: progress,
      duration: 300,
      useNativeDriver: false,
    }).start();
  }, [progress]);

  const widthInterpolation = animatedWidth.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.uploadProgressContainer}>
      <Text style={styles.uploadStatusText}>{statusText}</Text>
      <View style={styles.progressBarBackground}>
        <Animated.View 
  style={[styles.progressBarFill, { width: widthInterpolation }]} 
>
          {/* Progress text inside the bar */}
          <Text style={styles.progressTextInside}>{Math.round(progress)}%</Text>
        </Animated.View>
      </View>
      <ActivityIndicator size="small" color="#e68998" style={{ marginTop: 15 }} />
    </View>
  );
};

export default function HomeScreen() {
  const [inputText, setInputText] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatusText, setUploadStatusText] = useState('Initializing upload...');
  
  const userName = 'Prism'; 

  const router = useRouter(); 

  const animatedValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.loop(
      Animated.timing(animatedValue, {
        toValue: 1,
        duration: 6600,
        useNativeDriver: false,
      })
    ).start();
  }, []);

  const start = {
    x: animatedValue.interpolate({
      inputRange: [0, 1],
      outputRange: [0, 1],
    }),
    y: 0,
  };

  const end = {
    x: animatedValue.interpolate({
      inputRange: [0, 1],
      outputRange: [1, 0],
    }),
    y: 1,
  };

  const uploadImagesToServer = async (assets: ImagePicker.ImagePickerAsset[]) => {
    setIsUploading(true);
    setUploadProgress(0);
    setUploadStatusText(`Preparing ${assets.length} images...`);

    const totalSteps = assets.length + 2; 
    let currentStep = 0;
    const UPLOAD_ENDPOINT = 'YOUR_CHROMA_DB_VECTOR_SERVER_ENDPOINT';
    
    const simulateDelay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

    for (const asset of assets) {
      currentStep++;
      const fileName = asset.fileName || `outfit-image-${Date.now()}.jpg`;
      const fileType = asset.mimeType || 'image/jpeg';
      const uri = asset.uri;

      setUploadStatusText(`Uploading image ${currentStep} of ${assets.length}: ${fileName}`);
      setUploadProgress(Math.floor((currentStep / totalSteps) * 100));

      try {
        /*
        const formData = new FormData();
        formData.append('file', {
          uri: Platform.OS === 'android' ? uri : uri.replace('file://', ''),
          type: fileType,
          name: fileName,
        } as any);
        formData.append('userId', userName); // Example of sending extra data

        const response = await fetch(UPLOAD_ENDPOINT, {
          method: 'POST',
          body: formData,
          // Add headers like 'Authorization' or 'Content-Type' if necessary
        });

        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }
        // const result = await response.json(); // Process server response
        */
        
        await simulateDelay(600); 
      } catch (error) {
        console.error('Upload error:', error);
        Alert.alert('Upload Failed', `Could not upload image. Please check server connection. Details: ${error}`);
        setIsUploading(false);
        return; 
      }
    }
    
    currentStep++;
    setUploadStatusText('Finding your fashion twin...');
    setUploadProgress(Math.floor((currentStep / totalSteps) * 100));
    await simulateDelay(1500); 

    currentStep++;
    setUploadStatusText('Redirecting to model analysis...');
    setUploadProgress(100);
    await simulateDelay(500); 

    setIsUploading(false);
    router.push("/screens/model"); 
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
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      uploadImagesToServer(result.assets);
    } else if (result.canceled) {
      console.log('User cancelled image selection.');
    }
  };

  const handleMyCloset = () => {
    console.log('My Closet button pressed!');
  };

  const handleProfilePress = () => {
    console.log('Profile picture pressed!');
  };

  const handleAskAI = () => {
    console.log('Asking AI:', inputText);
    setInputText('');
  };

  const handleGoToModel = () => {
    router.push("/screens/model"); 
  };
  
  const handleGoToRecommend = () => {
    router.push("/screens/recommend"); 
  };

  return (
    <ImageBackground source={splashBg} style={styles.background}>
      {/* Semi-transparent overlay */}
      <LinearGradient
        colors={['rgba(255,255,255,0.05)', 'rgba(255,255,255,0.05)']}
        style={StyleSheet.absoluteFillObject}
      />

      <KeyboardAvoidingView
        style={styles.keyboardAvoidingContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Disable dismissal of keyboard when uploading */}
        <TouchableWithoutFeedback onPress={Keyboard.dismiss} disabled={isUploading}>
          <View style={styles.scrollContentContainer}>
            {/* Profile Picture (always visible) */}
            <View style={styles.topRightProfile}>
              <TouchableOpacity onPress={handleProfilePress} style={styles.profileContainer}>
                <View style={styles.profilePicBorder}>
                  <Image source={profilePic} style={styles.profilePic} />
                </View>
              </TouchableOpacity>
            </View>

            {/* Main Content Box */}
            <View style={styles.contentBox}>
              {/* Conditional rendering based on upload state */}
              {isUploading ? (
                <UploadProgressView progress={uploadProgress} statusText={uploadStatusText} />
              ) : (
                <>
                  <Text style={styles.greetingText}>
                    Hey {userName}, ask me anything about your style! ✨
                  </Text>

                  {/* AI Input Field with Send button */}
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

                  {/* Buttons Row */}
                  <View style={styles.buttonsRow}>
                    {/* Upload New Outfit Button with flowy gradient */}
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

                    {/* My Closet Button */}
                    <TouchableOpacity
                      style={styles.myClosetButton}
                      onPress={handleMyCloset}
                    >
                      <MaterialCommunityIcons name="hanger" size={22} color="#e68998" style={styles.iconStyle} />
                      <Text style={styles.buttonText}>My Closet</Text>
                    </TouchableOpacity>
                  </View>
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
  samsungPrismText: {
    position: 'absolute', 
    bottom: 20,
    marginBottom:10,
    fontSize: 18.5,
    color: '#ffffff',
    letterSpacing: 1,
  },
  tempButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginTop: 15,
    gap: 10,
  },
  uploadProgressContainer: {
    width: '100%',
    alignItems: 'center',
    paddingVertical: 40,
  },
  uploadStatusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
    textAlign: 'center',
  },
  progressBarBackground: {
    height: 30,
    width: '90%',
    backgroundColor: '#f0f0f0',
    borderRadius: 15,
    overflow: 'hidden',
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#e68998',
    justifyContent: 'center',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#d07988ff',
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'flex-end',
    paddingHorizontal: 10,
    minWidth: 50,
  },
  progressTextInside: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFF', 
  }
});