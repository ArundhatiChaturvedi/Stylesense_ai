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
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome5, Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
// 1. IMPORT useRouter from expo-router
import { useRouter } from 'expo-router'; 

const AnimatedLinearGradient = Animated.createAnimatedComponent(LinearGradient);

// NOTE: Please ensure these paths are correct, based on your previous fixes
const profilePic = require("../assets/images/profile_pic.png"); 
const splashBg = require("../assets/images/splash_bg.png");  

export default function HomeScreen() {
  const [inputText, setInputText] = useState('');
  const userName = 'Prism'; 

  const router = useRouter(); 

  // Gradient animation setup
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

  const handleUploadNewOutfit = () => {
    console.log('Upload New Outfit button pressed!');
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
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.scrollContentContainer}>
            {/* Profile Picture */}
            <View style={styles.topRightProfile}>
              <TouchableOpacity onPress={handleProfilePress} style={styles.profileContainer}>
                <View style={styles.profilePicBorder}>
                  <Image source={profilePic} style={styles.profilePic} />
                </View>
              </TouchableOpacity>
            </View>

            {/* Main Content Box */}
            <View style={styles.contentBox}>
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
              
              {/* 4. TEMPORARY NAVIGATION BUTTONS */}
              <View style={styles.tempButtonsRow}>
                <TouchableOpacity onPress={handleGoToModel} style={styles.tempButton}>
                  <Text style={styles.tempButtonText}>Go to Model.tsx</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={handleGoToRecommend} style={styles.tempButton}>
                  <Text style={styles.tempButtonText}>Go to Recommend.tsx</Text>
                </TouchableOpacity>
              </View>
              {/* END TEMPORARY NAVIGATION BUTTONS */}
              
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
    borderColor: '#e68998',
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
    marginBottom: 10, // Added margin to separate rows
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
  // NEW STYLES FOR TEMPORARY BUTTONS
  tempButtonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginTop: 15,
    gap: 10,
  },
  tempButton: {
    flex: 1,
    backgroundColor: '#3498db', // A distinct color for testing
    borderRadius: 15,
    paddingVertical: 8,
    alignItems: 'center',
  },
  tempButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  }
});