import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface UploadProgressViewProps {
  progress: number;
  statusText: string;
}

export const UploadProgressView: React.FC<UploadProgressViewProps> = ({ progress, statusText }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.statusText}>{statusText}</Text>
      <View style={styles.progressBarBackground}>
        <View 
          style={[
            styles.progressBarFill, 
            { width: `${Math.max(progress, 10)}%` }
          ]}
        >
          <Text style={styles.progressText}>{progress}%</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    alignItems: 'center',
    paddingVertical: 40,
  },
  statusText: {
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
  progressText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFF',
  },
});