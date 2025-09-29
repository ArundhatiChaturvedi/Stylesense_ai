import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ImageBackground } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useUser } from '../../contexts/UserContext';

const splashBg = require('../../assets/images/splash_bg.png');

export default function ProfileScreen() {
  const router = useRouter();
  const { userId, userStatus } = useUser();

  return (
    <ImageBackground source={splashBg} style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Profile</Text>
      </View>
      
      <View style={styles.content}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>User Information</Text>
          <Text style={styles.cardText}>User ID: {userId}</Text>
          {userStatus && (
            <>
              <Text style={styles.cardText}>
                Wardrobe Items: {userStatus.wardrobe_items_count}
              </Text>
              <Text style={styles.cardText}>
                Purchase History: {userStatus.purchase_history_count}
              </Text>
              <Text style={styles.cardText}>
                Total Items: {userStatus.total_items}
              </Text>
            </>
          )}
        </View>
        
        <View style={styles.card}>
          <Text style={styles.cardTitle}>About StyleSense AI</Text>
          <Text style={styles.cardText}>
            Your personal AI style assistant powered by Samsung Prism
          </Text>
        </View>
      </View>
      
      <Text style={styles.samsungPrismText}>SAMSUNG PRISM</Text>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    paddingTop: 50,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
  },
  backButton: {
    marginRight: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    padding: 20,
    borderRadius: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  cardText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 5,
  },
  samsungPrismText: {
    textAlign: 'center',
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 20,
  },
});