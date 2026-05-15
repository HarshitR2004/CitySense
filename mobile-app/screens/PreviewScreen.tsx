import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  Image,
  ScrollView,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { GlowingButton } from '../components/ui/GlowingButton';
import { LocationCard } from '../components/LocationCard';
import { reverseGeocodeLocation } from '../services/locationService';
import { submitComplaint } from '../services/apiService';
import { CameraView, useCameraPermissions } from 'expo-camera';

export function PreviewScreen({ route, navigation }: any) {
  const { imageUri, coords, fromCamera } = route.params || {};
  const [address, setAddress] = useState<string>('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [locationLoading, setLocationLoading] = useState(true);
  const [capturedImage, setCapturedImage] = useState<string | null>(imageUri || null);
  const [cameraRef, setCameraRef] = useState<any>(null);
  const [permission, requestPermission] = useCameraPermissions();

  useEffect(() => {
    getAddress();
    if (fromCamera && !imageUri) {
      requestPermission();
    }
  }, []);

  const getAddress = async () => {
    if (coords) {
      const addr = await reverseGeocodeLocation(
        coords.latitude,
        coords.longitude
      );
      setAddress(addr || 'Unknown location');
      setLocationLoading(false);
    }
  };

  const handleTakePicture = async () => {
    if (cameraRef) {
      try {
        const photo = await cameraRef.takePictureAsync();
        setCapturedImage(photo.uri);
      } catch (error) {
        alert('Error taking picture');
      }
    }
  };

  const handleSubmit = async () => {

    if (!capturedImage) {
      alert('Please capture or select an image');
      return;
    }

    setLoading(true);
    try {
      const result = await submitComplaint({
        imageUri: capturedImage,
        latitude: coords.latitude,
        longitude: coords.longitude,
        address: address,
        description,
      });

      navigation.navigate('Success', { trackingId: result.reportId });
    } catch (error) {
      alert('Error submitting complaint. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (fromCamera && !capturedImage) {
    if (!permission?.granted) {
      return (
        <View style={{ flex: 1, backgroundColor: '#09090b', alignItems: 'center', justifyContent: 'center' }}>
          <Text style={{ fontFamily: 'PlusJakartaSans_400Regular', color: '#E2FF31', marginBottom: 16 }}>
            CAMERA PERMISSION REQUIRED
          </Text>
          <GlowingButton
            label="GRANT ACCESS"
            onPress={requestPermission}
            variant="primary"
          />
        </View>
      );
    }

    return (
      <View style={{ flex: 1, backgroundColor: '#09090b' }}>
        <CameraView
          ref={setCameraRef}
          style={{ flex: 1 }}
        />
        <View style={{ position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(9,9,11,0.9)', paddingHorizontal: 24, paddingVertical: 16, gap: 12 }}>
          <GlowingButton
            label="CAPTURE"
            onPress={handleTakePicture}
            size="lg"
            variant="primary"
          />
          <GlowingButton
            label="ABORT"
            onPress={() => navigation.goBack()}
            size="md"
            variant="secondary"
          />
        </View>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={{ flex: 1, backgroundColor: '#09090b' }}
    >
      <ScrollView style={{ flex: 1 }}>
        <View style={{ flex: 1, paddingHorizontal: 24, paddingTop: 64, paddingBottom: 48, gap: 24 }}>
          {/* Header */}
          <View>
            <Text style={{
              fontFamily: 'Unbounded_700Bold',
              fontSize: 24,
              color: '#FAFAFA',
              marginBottom: 8,
              textTransform: 'uppercase',
            }}>
              DATA PREVIEW
            </Text>
            <Text style={{
              fontFamily: 'PlusJakartaSans_400Regular',
              color: '#A1A1AA',
            }}>
            </Text>
          </View>

          {/* Image Preview */}
          {capturedImage && (
            <View style={{
              backgroundColor: '#18181b',
              borderWidth: 1,
              borderColor: '#27272a',
              padding: 8,
            }}>
              <Image
                source={{ uri: capturedImage }}
                style={{ width: '100%', height: 256 }}
                resizeMode="cover"
              />
            </View>
          )}

          {/* Location Card */}
          <LocationCard
            address={address}
            latitude={coords?.latitude}
            longitude={coords?.longitude}
            isLoading={locationLoading}
          />

          {/* Description Input */}
          <View>
            <Text style={{
              fontFamily: 'Unbounded_400Regular',
              color: '#E2FF31',
              fontSize: 12,
              marginBottom: 8,
              textTransform: 'uppercase',
            }}>
              Additional Information
            </Text>
            <TextInput
              style={{
                backgroundColor: '#18181b',
                borderWidth: 1,
                borderColor: '#27272a',
                padding: 16,
                color: '#FAFAFA',
                minHeight: 120,
                textAlignVertical: 'top',
                fontFamily: 'PlusJakartaSans_400Regular',
                fontSize: 16,
              }}
              placeholder="Describe your issue..."
              placeholderTextColor="#71717a"
              value={description}
              onChangeText={setDescription}
              multiline
              maxLength={500}
            />
            <Text style={{
              fontFamily: 'PlusJakartaSans_400Regular',
              color: '#71717a',
              fontSize: 12,
              marginTop: 8,
              textAlign: 'right',
            }}>
              {description.length}/500
            </Text>
          </View>

          {/* Submit Button */}
          <GlowingButton
            label="REPORT"
            onPress={handleSubmit}
            loading={loading}
            size="lg"
            variant="primary"
          />

          {/* Back Button */}
          <GlowingButton
            label="ABORT"
            onPress={() => navigation.goBack()}
            disabled={loading}
            size="md"
            variant="secondary"
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
