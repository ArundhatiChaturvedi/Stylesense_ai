import React, { useEffect, useState } from 'react';
import { useLocalSearchParams, useRouter } from 'expo-router';
import {
  View,
  Text,
  ScrollView,
  ImageBackground,
  TouchableOpacity,
  Alert,
  Linking,
  StyleSheet,
  Image
} from 'react-native';
import { MaterialCommunityIcons, Ionicons } from '@expo/vector-icons';
import { StyleRecommendation } from '../services/api';

const splashBg = require('../../assets/images/splash_bg.png');

export default function RecommendScreen() {
  const params = useLocalSearchParams();
  const router = useRouter();
  const [recommendation, setRecommendation] = useState<StyleRecommendation | null>(null);
  const [userPrompt, setUserPrompt] = useState<string>('');

  useEffect(() => {
    if (params.recommendation) {
      try {
        const recommendationData = JSON.parse(params.recommendation as string);
        setRecommendation(recommendationData);
      } catch (error) {
        console.error('Error parsing recommendation data:', error);
        Alert.alert('Error', 'Failed to load recommendation data');
      }
    }
    
    if (params.userPrompt) {
      setUserPrompt(params.userPrompt as string);
    }
  }, [params]);

  const handleLinkPress = async (url: string) => {
    try {
      const supported = await Linking.canOpenURL(url);
      if (supported) {
        await Linking.openURL(url);
      } else {
        Alert.alert('Error', 'Unable to open link');
      }
    } catch (error) {
      console.error('Link opening error:', error);
      Alert.alert('Error', 'Failed to open link');
    }
  };

  const handleBackPress = () => {
    router.back();
  };

  if (!recommendation) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading your style recommendation...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ImageBackground source={splashBg} style={styles.backgroundImage}>
        <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.scrollContent}>
          {/* Header */}
          <View style={styles.header}>
            <TouchableOpacity onPress={handleBackPress} style={styles.backButton}>
              <Ionicons name="arrow-back" size={28} color="#fff" />
            </TouchableOpacity>
            <Text style={styles.headerTitle}>Your Style Guide</Text>
          </View>

          {/* User Prompt Display */}
          {userPrompt && (
            <View style={styles.promptCard}>
              <Text style={styles.promptLabel}>Your Request:</Text>
              <Text style={styles.promptText}>{userPrompt}</Text>
            </View>
          )}

          {/* Celebrity Twin Section */}
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <MaterialCommunityIcons name="star-circle" size={28} color="#e68998" />
              <Text style={styles.cardTitle}>Your Celebrity Style Twin</Text>
            </View>
            <Text style={styles.celebrityName}>{recommendation.celebrity_twin}</Text>
            {recommendation.celebrity_image_url && (
              <Image 
                source={{ uri: recommendation.celebrity_image_url }} 
                style={styles.celebrityImage}
                resizeMode="cover"
              />
            )}
            <View style={styles.emotionBadge}>
              <Text style={styles.emotionText}>Mood: {recommendation.extracted_emotion}</Text>
            </View>
          </View>

          {/* Weather Info */}
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Ionicons name="sunny" size={26} color="#e68998" />
              <Text style={styles.cardTitle}>Weather Consideration</Text>
            </View>
            <Text style={styles.weatherText}>{recommendation.weather_info}</Text>
          </View>

          {/* Items You Own */}
          {recommendation.items_owned && recommendation.items_owned.length > 0 && (
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <MaterialCommunityIcons name="hanger" size={26} color="#e68998" />
                <Text style={styles.cardTitle}>From Your Wardrobe</Text>
              </View>
              {recommendation.items_owned.map((item, index) => (
                <View key={index} style={styles.itemCard}>
                  <View style={styles.itemHeader}>
                    <Ionicons name="checkmark-circle" size={20} color="#4CAF50" />
                    <Text style={styles.itemLabel}>{item.item}</Text>
                  </View>
                  <Text style={styles.itemDescription}>{item.owned_item}</Text>
                  <View style={styles.confidenceBar}>
                    <View 
                      style={[
                        styles.confidenceFill, 
                        { width: `${(item.confidence || 0) * 100}%` }
                      ]} 
                    />
                  </View>
                  <Text style={styles.confidenceText}>
                    Match: {((item.confidence || 0) * 100).toFixed(0)}%
                  </Text>
                </View>
              ))}
            </View>
          )}

          {/* Items to Buy */}
          {recommendation.items_to_buy && recommendation.items_to_buy.length > 0 && (
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <MaterialCommunityIcons name="shopping" size={26} color="#e68998" />
                <Text style={styles.cardTitle}>Suggested Additions</Text>
              </View>
              {recommendation.items_to_buy.map((item, index) => (
                <View key={index} style={styles.itemCard}>
                  <View style={styles.itemHeader}>
                    <Ionicons name="cart" size={20} color="#e68998" />
                    <Text style={styles.itemLabel}>{item.item}</Text>
                  </View>
                  <Text style={styles.itemDescription}>{item.suggested_product}</Text>
                  {item.brand && (
                    <Text style={styles.brandText}>Brand: {item.brand}</Text>
                  )}
                  {item.link && (
                    <TouchableOpacity 
                      style={styles.shopButton}
                      onPress={() => handleLinkPress(item.link)}
                    >
                      <Text style={styles.shopButtonText}>Shop Now</Text>
                      <Ionicons name="open-outline" size={16} color="#fff" />
                    </TouchableOpacity>
                  )}
                  <View style={styles.confidenceBar}>
                    <View 
                      style={[
                        styles.confidenceFill, 
                        { width: `${(item.confidence || 0) * 100}%` }
                      ]} 
                    />
                  </View>
                  <Text style={styles.confidenceText}>
                    Relevance: {((item.confidence || 0) * 100).toFixed(0)}%
                  </Text>
                </View>
              ))}
            </View>
          )}

          {/* Final Recommendation */}
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <MaterialCommunityIcons name="lightbulb" size={26} color="#e68998" />
              <Text style={styles.cardTitle}>Styling Advice</Text>
            </View>
            <Text style={styles.finalRecommendation}>
              {recommendation.final_recommendation}
            </Text>
          </View>

          {/* Action Buttons */}
          <View style={styles.actionButtons}>
            <TouchableOpacity 
              style={styles.primaryButton}
              onPress={handleBackPress}
            >
              <Text style={styles.primaryButtonText}>Get Another Recommendation</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.bottomSpacing} />
        </ScrollView>
      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  backgroundImage: {
    flex: 1,
    resizeMode: 'cover',
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    fontSize: 18,
    color: '#333',
    fontWeight: '600',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
  },
  backButton: {
    padding: 8,
    marginRight: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    flex: 1,
  },
  promptCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    marginHorizontal: 20,
    marginBottom: 15,
    padding: 15,
    borderRadius: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#e68998',
  },
  promptLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 5,
  },
  promptText: {
    fontSize: 16,
    color: '#333',
    fontStyle: 'italic',
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    marginHorizontal: 20,
    marginBottom: 15,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 10,
  },
  celebrityName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#e68998',
    textAlign: 'center',
    marginBottom: 15,
  },
  celebrityImage: {
    width: '100%',
    height: 250,
    borderRadius: 12,
    marginBottom: 15,
  },
  emotionBadge: {
    backgroundColor: '#fff0f5',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'center',
    borderWidth: 1,
    borderColor: '#e68998',
  },
  emotionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#e68998',
    textTransform: 'capitalize',
  },
  weatherText: {
    fontSize: 16,
    color: '#555',
    lineHeight: 24,
  },
  itemCard: {
    backgroundColor: '#f9f9f9',
    padding: 15,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  itemLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginLeft: 8,
    flex: 1,
  },
  itemDescription: {
    fontSize: 15,
    color: '#555',
    marginBottom: 8,
    lineHeight: 22,
  },
  brandText: {
    fontSize: 14,
    color: '#777',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  shopButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#e68998',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 8,
    marginTop: 8,
    marginBottom: 8,
  },
  shopButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginRight: 6,
  },
  confidenceBar: {
    height: 6,
    backgroundColor: '#e0e0e0',
    borderRadius: 3,
    overflow: 'hidden',
    marginTop: 8,
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
  },
  confidenceText: {
    fontSize: 12,
    color: '#777',
    marginTop: 4,
  },
  finalRecommendation: {
    fontSize: 16,
    color: '#333',
    lineHeight: 26,
    textAlign: 'justify',
  },
  actionButtons: {
    paddingHorizontal: 20,
    marginTop: 10,
  },
  primaryButton: {
    backgroundColor: '#e68998',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  bottomSpacing: {
    height: 20,
  },
});