import { Platform } from 'react-native';

const defaultHost = Platform.OS === 'android' ? '10.0.2.2' : 'localhost';
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || `http://${defaultHost}:8000/api/v1`;

export interface ComplaintPayload {
  imageUri: string;
  latitude: number;
  longitude: number;
  address: string;
  description: string;
}

export async function submitComplaint(payload: ComplaintPayload) {
  try {
    if (!payload.imageUri) {
      throw new Error('Missing image URI');
    }

    const formData = new FormData();

    if (Platform.OS === 'web') {
      const imageResponse = await fetch(payload.imageUri);
      if (!imageResponse.ok) {
        throw new Error('Unable to load image for upload');
      }

      const imageBlob = await imageResponse.blob();
      formData.append('file', imageBlob, 'issue.jpg');
    } else {
      formData.append('file', {
        uri: payload.imageUri,
        type: 'image/jpeg',
        name: 'issue.jpg',
      } as any);
    }

    formData.append('latitude', payload.latitude.toString());
    formData.append('longitude', payload.longitude.toString());

    console.log('Sending request to:', `${API_BASE_URL}/analyze`);
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
      // Do not set Content-Type manually, fetch will set it with the correct boundary
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Server error response:', errorText);
      throw new Error(`HTTP Error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}
