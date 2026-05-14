import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React from 'react';
import { HomeScreen } from '../../screens/HomeScreen';
import { PreviewScreen } from '../../screens/PreviewScreen';
import { SuccessScreen } from '../../screens/SuccessScreen';

const Stack = createNativeStackNavigator();

export default function RootLayout() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animationEnabled: true,
        cardStyle: { backgroundColor: '#0a0e27' },
      }}
    >
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Preview" component={PreviewScreen} />
      <Stack.Screen name="Success" component={SuccessScreen} />
    </Stack.Navigator>
  );
}
