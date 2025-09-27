import React, { useState } from 'react';
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
  ScrollView
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

import { FontAwesome5, MaterialCommunityIcons } from '@expo/vector-icons';

const profilePic = require("../assets/images/profile_pic.png"); 
const splashBg = require("../assets/images/splash_bg.png");  

export default function HomeScreen() {
  const [inputText, setInputText] = useState('');
  const userName = 'Prism'; 

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

  return (
    <ImageBackground source={splashBg} style={styles.background}>
      {/* Semi-transparent overlay */}
      <LinearGradient
        colors={['rgba(255,255,255,0.15)', 'rgba(255,255,255,0.05)']}
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

              {/* AI Input Field */}
              <View style={styles.aiInputWrapper}>
                <TextInput
                  style={styles.aiInputField}
                  placeholder="Looking for inspiration? Try asking me.."
                  placeholderTextColor="#B0B0B0"
                  value={inputText}
                  onChangeText={setInputText}
                  onSubmitEditing={handleAskAI}
                  multiline={true}
                  numberOfLines={4}
                  textAlignVertical="top"
                />
              </View>

              {/* Buttons Row */}
              <View style={styles.buttonsRow}>
                {/* Upload New Outfit Button */}
                <TouchableOpacity
                  style={styles.uploadButton}
                  onPress={handleUploadNewOutfit}
                >
                  <FontAwesome5 name="camera" size={20} color="#FFF" style={styles.iconStyle} />
                  <Text style={[styles.buttonText, { color: '#FFF' }]}>Upload Outfit</Text>
                </TouchableOpacity>

                {/* My Closet Button */}
                <TouchableOpacity
                  style={styles.myClosetButton}
                  onPress={handleMyCloset}
                >
                  <MaterialCommunityIcons name="hanger" size={22} color="#e68998ff" style={styles.iconStyle} />
                  <Text style={styles.buttonText}>My Closet</Text>
                </TouchableOpacity>
              </View>
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
    borderColor: '#e68998ff',
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
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
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
    backgroundColor: '#f0f0f0ff',
    borderRadius: 15,
    paddingHorizontal: 15,
    paddingVertical: 10,
    marginBottom: 25,
    width: '100%',
    minHeight: 100,
  },
  aiInputField: {
    flex: 1,
    minHeight: 80,
    fontSize: 16,
    color: '#333',
    textAlignVertical: 'top',
  },
  buttonsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    gap: 10,
  },
  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e68998ff', 
    borderRadius: 20,
    paddingVertical: 12,
    paddingHorizontal: 15,
    flex: 1,
    justifyContent: 'center',
    shadowColor: '#FF91A4',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 5,
    elevation: 4,
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
    borderColor: '#eeb3b3ff',
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
});

