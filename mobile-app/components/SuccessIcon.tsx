import React, { useEffect } from 'react';
import { View } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withSequence,
  withDelay,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export function SuccessIcon() {
  const scale = useSharedValue(0);
  const opacity = useSharedValue(0);

  useEffect(() => {
    scale.value = withSequence(
      withDelay(100, withSpring(1, { damping: 6 }))
    );
    opacity.value = withDelay(100, withSpring(1));
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <Animated.View style={animatedStyle}>
      <LinearGradient
        colors={['#0099ff', '#00d9ff']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={{
          width: 96,
          height: 96,
          borderRadius: 48,
          alignItems: 'center',
          justifyContent: 'center',
          shadowColor: '#00d9ff',
          shadowOffset: { width: 0, height: 0 },
          shadowOpacity: 0.4,
          shadowRadius: 30,
          elevation: 20,
        }}
      >
        <MaterialCommunityIcons name="check" size={48} color="white" />
      </LinearGradient>
    </Animated.View>
  );
}
