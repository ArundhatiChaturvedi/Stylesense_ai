import React from 'react';
import {
  StyleSheet,
  View,
  Text,
  ImageBackground,
  Image,
  ScrollView, 
  Linking,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { MaterialCommunityIcons } from '@expo/vector-icons'; 

const { width: SCREEN_W } = Dimensions.get('window');

const splashBg = require("../../assets/images/splash_bg.png"); 
const celebImage = require("../../assets/images/margo.jpg"); 

const SASSAFRAS_LINK = "https://www.google.com/search?q=http://myntra.com/product/SASSAFRAS";
const ROADSTER_LINK = "https://www.google.com/search?q=http://myntra.com/product/Roadster";

export default function RecommendScreen() {
  const router = useRouter(); 

  const handleLinkPress = (url: string) => {
    Linking.openURL(url).catch(err => console.error("Couldn't load page", err));
  };

  return (
    <View style={styles.fullScreenContainer}>
      <ImageBackground source={splashBg} style={styles.background}>
        <LinearGradient
          colors={['rgba(255,255,255,0.05)', 'rgba(255,255,255,0.05)']}
          style={StyleSheet.absoluteFillObject}
        />
        
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.spacer} /> 

          <View style={styles.contentBox}>
            
            {/* Image Section */}
            <View style={styles.imageSection}>
              <Image 
                source={celebImage} 
                style={[
                  styles.celebImageBase, 
                  { width: '50%', aspectRatio: 0.5 }
                ]} 
              />
            </View>

            <View style={styles.textBlock}>
              <Text style={styles.paragraph}>
                That sounds like a fabulous night out! Getting dressed to feel chic and sparkly for a party is the perfect mood. We've channeled your inner Fashionista —she masters high-glamour looks that still feel elegant and effortless, blending classic silhouettes with perfect amounts of sparkle.
              </Text>

              <Text style={styles.heading}>
                Here is your StyleSense look, bridging your wardrobe with the latest must-have pieces:
              </Text>

              <View style={styles.listItem}>
                <MaterialCommunityIcons name="check-circle-outline" size={20} color="#60C08D" style={styles.checkIcon} />
                <Text style={styles.listItemText}>
                  <Text style={styles.boldText}>Use from Your Wardrobe:</Text> Black Leather Clutch Bag, small size, minimalist design, perfect for evening. (Use this to hold your essentials; its clean lines will anchor the sparkle.)
                </Text>
              </View>

              <Text style={[styles.heading, { marginTop: 15 }]}>
                🛍 New Pieces to Buy:
              </Text>
              
              <View style={styles.listItem}>
                <MaterialCommunityIcons name="shopping" size={20} color="#e68998" style={styles.shopIcon} />
                <Text style={styles.listItemText}>
                  <Text style={styles.boldText}>Sequin Embellished A-line Dress, Rose Gold </Text>
                  <Text style={styles.linkText} onPress={() => handleLinkPress(SASSAFRAS_LINK)}>(by SASSAFRAS)</Text>: This dress is the core of your sparkle. The A-line cut is flattering and feels sophisticated.
                </Text>
              </View>

              <View style={styles.listItem}>
                <MaterialCommunityIcons name="shopping" size={20} color="#e68998" style={styles.shopIcon} />
                <Text style={styles.listItemText}>
                  <Text style={styles.boldText}>Pointed-toe Slingback Heels, Black Suede </Text>
                  <Text style={styles.linkText} onPress={() => handleLinkPress(ROADSTER_LINK)}>(by Roadster)</Text>: These will elongate your legs and contrast perfectly with the rose gold sequins for maximum chicness.
                </Text>
              </View>

              <Text style={[styles.heading, { marginTop: 20 }]}>
                Styling Tip:
              </Text>
              <Text style={styles.paragraph}>
                Since the weather in Vellore, India is 28°C and Sunny with high humidity, you can skip the coat! Keep accessories minimal—a delicate layered necklace and small diamond studs will complete this high-glamour, chic look without being overdone.
              </Text>
            </View>
          </View>
        </ScrollView>

        <Text style={styles.samsungPrismText}>SAMSUNG PRISM</Text>

      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  fullScreenContainer: {
    flex: 1,
  },
  background: {
    flex: 1,
    resizeMode: 'cover',
  },

  scrollView: {
    flex: 1,
    width: '100%',
  },
  scrollContent: {
    alignItems: 'center',
    paddingBottom: 80, 
  },
  spacer: {
    height: 50, 
  },

  contentBox: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 25,
    padding: 20, 
    width: SCREEN_W * 0.9, 
    maxWidth: 400,
    marginBottom: 40,
    elevation: 5,
  },

  imageSection: {
    width: '100%',
    alignItems: 'center',
    marginBottom: 20,
  },
  celebImageBase: {
    borderRadius: 12,
    resizeMode: 'cover',
  },

  textBlock: {
    width: '100%',
  },
  paragraph: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
    marginBottom: 15,
  },
  heading: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  boldText: {
    fontWeight: 'bold',
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  listItemText: {
    flex: 1,
    fontSize: 15,
    color: '#333',
    lineHeight: 22,
  },
  checkIcon: {
    marginRight: 8,
    marginTop: 2, 
  },
  shopIcon: {
    marginRight: 8,
    marginTop: 2, 
  },
  linkText: {
    color: '#e68998', 
    fontWeight: 'bold',
    textDecorationLine: 'underline',
  },

  samsungPrismText: {
    position: 'absolute',
    bottom: 20,
    alignSelf: 'center',
    fontSize: 18.5,
    color: '#ffffff',
    letterSpacing: 1,
    zIndex: 50,
  },
});
