import React from 'react';
import { View, Text, StyleSheet, ImageBackground, Image } from 'react-native';

const Splash: React.FC = () => {
  return (
    <ImageBackground
      source={require("../assets/images/splash_bg.png")} 
      style={styles.container}
    >
      <Image
        source={require("../assets/images/models.png")} 
        style={styles.modelImage}
      />

      <Text style={styles.mainText}>STYLE SENSE AI</Text>
      <Text style={styles.subText}>YOUR PERSONAL RECOMMENDATION APP</Text>

      <View style={styles.bottomContainer}>
        <Text style={styles.samsungPrismText}>SAMSUNG PRISM</Text>
      </View>
    </ImageBackground>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modelImage: {
    width: 320,
    height: 420,
    resizeMode: 'contain',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 10,
  },
  mainText: {
    fontFamily: 'BubbleBobble',
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    textShadowColor: 'rgba(0, 0, 0, 0.4)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 5,
    marginBottom: 5,
    letterSpacing: 1.5,
  },
  subText: {
    fontSize: 16,
    color: '#E8E8E8',
    fontWeight: '700',
    textShadowColor: 'rgba(0, 0, 0, 0.5)', 
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 4,
    marginBottom: 80,
    letterSpacing: 1,
  },
  bottomContainer: {
    position: 'absolute',
    bottom: 30,
  },
  samsungPrismText: {
    fontSize: 20,
    color: '#FFFFFF',
    opacity: 0.8,
    letterSpacing: 1,
  },
});

export default Splash;
