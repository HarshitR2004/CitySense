import React from 'react';
import { View, ViewProps } from 'react-native';

interface GlowingCardProps extends ViewProps {
  children: React.ReactNode;
  intensity?: 'sm' | 'md' | 'lg';
}

export function GlowingCard({
  children,
  intensity = 'md',
  style,
  ...props
}: GlowingCardProps) {

  // Brutalist sharp shadow intensity
  const offset = intensity === 'lg' ? 8 : intensity === 'md' ? 6 : 4;

  return (
    <View
      style={[{
        borderRadius: 0,
        backgroundColor: '#18181b', // zinc-900
        borderWidth: 1,
        borderColor: '#27272a', // zinc-800
        shadowColor: '#000000',
        shadowOffset: { width: offset, height: offset },
        shadowOpacity: 1,
        shadowRadius: 0,
        elevation: offset * 2,
      }, style]}
      {...props}
    >
      {children}
    </View>
  );
}
