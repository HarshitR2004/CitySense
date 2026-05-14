import * as ImagePicker from 'expo-image-picker';

export async function pickImageFromGallery() {
  try {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      return result.assets[0].uri;
    }
    return null;
  } catch (error) {
    console.error('Gallery picker error:', error);
    return null;
  }
}
