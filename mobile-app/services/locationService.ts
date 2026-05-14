import * as Location from 'expo-location';

export async function requestLocationPermissions() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  return status === 'granted';
}

export async function getCurrentLocation() {
  try {
    const location = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced,
    });
    return location.coords;
  } catch (error) {
    console.error('Location error:', error);
    return null;
  }
}

export async function reverseGeocodeLocation(
  latitude: number,
  longitude: number
) {
  try {
    const result = await Location.reverseGeocodeAsync({
      latitude,
      longitude,
    });
    if (result[0]) {
      const { street, city, region } = result[0];
      return `${street}, ${city}, ${region}`;
    }
    return null;
  } catch (error) {
    console.error('Geocode error:', error);
    return null;
  }
}
