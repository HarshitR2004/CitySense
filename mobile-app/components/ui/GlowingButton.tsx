import React from 'react';
import {
  TouchableOpacity,
  Text,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
  View,
} from 'react-native';
import * as Haptics from 'expo-haptics';
import Animated, { useAnimatedStyle, useSharedValue, withSpring } from 'react-native-reanimated';

interface ActionButtonProps {
  label: string;
  onPress: () => void | Promise<void>;
  loading?: boolean;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

export function GlowingButton({
  label,
  onPress,
  loading = false,
  disabled = false,
  size = 'md',
  variant = 'primary',
  style,
  textStyle,
}: ActionButtonProps) {
  const scale = useSharedValue(1);

  const paddingMap = {
    sm: { paddingHorizontal: 16, paddingVertical: 12 },
    md: { paddingHorizontal: 24, paddingVertical: 16 },
    lg: { paddingHorizontal: 32, paddingVertical: 20 },
  };

  const textSizeMap = {
    sm: { fontSize: 14 },
    md: { fontSize: 16 },
    lg: { fontSize: 18 },
  };

  const handlePressIn = () => {
    if (!disabled && !loading) {
      scale.value = withSpring(0.96, { damping: 15, stiffness: 300 });
    }
  };

  const handlePressOut = () => {
    if (!disabled && !loading) {
      scale.value = withSpring(1, { damping: 15, stiffness: 300 });
    }
  };

  const handlePress = async () => {
    if (disabled || loading) return;
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    await onPress();
  };

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const isPrimary = variant === 'primary';

  return (
    <AnimatedTouchable
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      onPress={handlePress}
      disabled={disabled || loading}
      activeOpacity={1}
      style={[
        {
          borderRadius: 0, // Brutalist sharp corners
          borderWidth: isPrimary ? 0 : 2,
          borderColor: isPrimary ? 'transparent' : '#E2FF31',
          backgroundColor: isPrimary ? '#E2FF31' : 'transparent',
          ...paddingMap[size],
          alignItems: 'center',
          justifyContent: 'center',
          opacity: disabled ? 0.5 : 1,
        },
        animatedStyle,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={isPrimary ? '#09090b' : '#E2FF31'} />
      ) : (
        <Text
          style={[
            {
              color: isPrimary ? '#09090b' : '#E2FF31',
              fontFamily: 'Unbounded_700Bold',
              textTransform: 'uppercase',
              letterSpacing: 1,
              ...textSizeMap[size],
            },
            textStyle,
          ]}
        >
          {label}
        </Text>
      )}
    </AnimatedTouchable>
  );
}
