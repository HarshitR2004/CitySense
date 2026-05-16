import React, { useEffect } from 'react';
import { View, Text, ScrollView } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withDelay,
  withTiming,
  Easing,
} from 'react-native-reanimated';
import { GlowingButton } from '../components/ui/GlowingButton';
import { GlowingCard } from '../components/ui/GlowingCard';
import * as Location from 'expo-location';
import * as ImagePicker from 'expo-image-picker';
import { pickImageFromGallery } from '../services/galleryService';
import { getCurrentLocation } from '../services/locationService';

export function HomeScreen({ navigation }: any) {
  const headerOpacity = useSharedValue(0);
  const headerTranslateY = useSharedValue(20);
  
  const buttonsOpacity = useSharedValue(0);
  const buttonsTranslateY = useSharedValue(20);

  const footerOpacity = useSharedValue(0);
  const footerTranslateY = useSharedValue(20);

  useEffect(() => {
    const timingConfig = { duration: 600, easing: Easing.out(Easing.exp) };
    
    headerOpacity.value = withTiming(1, timingConfig);
    headerTranslateY.value = withTiming(0, timingConfig);

    buttonsOpacity.value = withDelay(150, withTiming(1, timingConfig));
    buttonsTranslateY.value = withDelay(150, withTiming(0, timingConfig));

    footerOpacity.value = withDelay(300, withTiming(1, timingConfig));
    footerTranslateY.value = withDelay(300, withTiming(0, timingConfig));

    requestPermissions();
  }, []);

  const animatedHeaderStyle = useAnimatedStyle(() => ({
    opacity: headerOpacity.value,
    transform: [{ translateY: headerTranslateY.value }],
  }));

  const animatedButtonsStyle = useAnimatedStyle(() => ({
    opacity: buttonsOpacity.value,
    transform: [{ translateY: buttonsTranslateY.value }],
  }));

  const animatedFooterStyle = useAnimatedStyle(() => ({
    opacity: footerOpacity.value,
    transform: [{ translateY: footerTranslateY.value }],
  }));

  const requestPermissions = async () => {
    await Location.requestForegroundPermissionsAsync();
    await ImagePicker.requestMediaLibraryPermissionsAsync();
  };

  const handleCapture = async () => {
    const location = await getCurrentLocation();
    if (location) {
      navigation.navigate('Preview', {
        imageUri: null,
        coords: location,
        fromCamera: true,
      });
    } else {
      alert('Unable to get location. Please enable location permissions.');
    }
  };

  const handleGallery = async () => {
    const imageUri = await pickImageFromGallery();
    if (imageUri) {
      const location = await getCurrentLocation();
      if (location) {
        navigation.navigate('Preview', {
          imageUri,
          coords: location,
          fromCamera: false,
        });
      } else {
        alert('Unable to get location. Please enable location permissions.');
      }
    }
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#09090b' }}>
      <View style={{ flex: 1, minHeight: '100%', paddingHorizontal: 24, paddingVertical: 64, justifyContent: 'flex-start' }}>
        
        {/* Header */}
        <Animated.View style={animatedHeaderStyle}>
          <View style={{ alignItems: 'flex-start', marginBottom: 48, marginTop: 40 }}>
            <View
              style={{
                width: 56,
                height: 56,
                backgroundColor: '#18181b',
                borderWidth: 2,
                borderColor: '#E2FF31',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 24,
              }}
            >
              <MaterialCommunityIcons
                name="crosshairs-gps"
                size={28}
                color="#E2FF31"
              />
            </View>
            <Text style={{
              fontFamily: 'Unbounded_700Bold',
              fontSize: 40,
              color: '#FAFAFA',
              marginBottom: 8,
              lineHeight: 48,
              textTransform: 'uppercase',
              letterSpacing: -1,
            }}>
              City
            </Text>
            <Text style={{
              fontFamily: 'Unbounded_400Regular',
              fontSize: 32,
              color: '#E2FF31',
              marginBottom: 16,
              lineHeight: 40,
              letterSpacing: 2,
            }}>
              SENSE
            </Text>
            <Text style={{
              fontFamily: 'PlusJakartaSans_400Regular',
              color: '#A1A1AA',
              fontSize: 16,
              lineHeight: 24,
            }}>
              Speak up about issues and help build a responsible community.
            </Text>
          </View>
        </Animated.View>

        {/* Buttons */}
        <Animated.View style={[animatedButtonsStyle, { gap: 10 }]}>
          <GlowingCard intensity="lg" style={{ padding: 24, marginBottom: 8 }}>
            <Text style={{
              fontFamily: 'Unbounded_700Bold',
              color: '#FAFAFA',
              fontSize: 16,
              marginBottom: 16,
            }}>
              NEW COMPLAINT
            </Text>
            <GlowingButton
              label="Open Camera"
              onPress={handleCapture}
              size="lg"
              variant="primary"
            />
          </GlowingCard>

          <GlowingButton
            label="Upload Image"
            onPress={handleGallery}
            size="lg"
            variant="secondary"
          />
        </Animated.View>


      </View>
    </ScrollView>
  );
}
