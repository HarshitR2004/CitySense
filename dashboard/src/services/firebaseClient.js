// Initializes Firebase Web SDK when Vite env vars are provided.
// Exports helper functions to read reports from Firestore.
import { initializeApp, getApps } from 'firebase/app';
import {
  getFirestore,
  collection,
  getDocs,
  doc,
  getDoc,
  query,
  orderBy,
  onSnapshot
} from 'firebase/firestore';

let firestore = null;

function initFirebase() {
  // Vite env variables start with VITE_
  const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
  const projectId = import.meta.env.VITE_FIREBASE_PROJECT_ID;
  const authDomain = import.meta.env.VITE_FIREBASE_AUTH_DOMAIN;
  const storageBucket = import.meta.env.VITE_FIREBASE_STORAGE_BUCKET;
  const appId = import.meta.env.VITE_FIREBASE_APP_ID;

  if (!apiKey || !projectId) {
    return null;
  }

  // Avoid re-initializing
  if (!getApps().length) {
    const config = {
      apiKey,
      authDomain,
      projectId,
      storageBucket,
      appId,
    };
    try {
      initializeApp(config);
    } catch (e) {
      console.warn('Firebase init failed', e);
      return null;
    }
  }

  try {
    firestore = getFirestore();
    return firestore;
  } catch (e) {
    console.warn('Failed to get Firestore instance', e);
    return null;
  }
}

// Lazy initialize
function getFirestoreClient() {
  if (firestore) return firestore;
  return initFirebase();
}

// Convert Firestore timestamp to ISO string safely
function toISO(value) {
  if (!value) return new Date().toISOString();
  // Firestore Timestamp has toDate() method
  if (typeof value.toDate === 'function') return value.toDate().toISOString();
  try {
    return new Date(value).toISOString();
  } catch (e) {
    return new Date().toISOString();
  }
}

function mapDocToReport(docSnap) {
  const data = docSnap.data();
  return {
    reportId: docSnap.id,
    imageUrl: data.imageUrl || data.image || '',
    annotatedImageUrl: data.annotatedImageUrl || data.annotatedImage || '',
    location: data.location || { latitude: 0, longitude: 0 },
    analysis: data.analysis || {},
    status: data.status || 'reported',
    task_id: data.task_id || data.taskId || null,
    createdAt: toISO(data.createdAt),
    updatedAt: toISO(data.updatedAt || data.createdAt),
  };
}

export async function fetchReportsFromFirestore() {
  const db = getFirestoreClient();
  if (!db) return null;

  const coll = collection(db, 'reports');
  const q = query(coll, orderBy('createdAt', 'desc'));
  const snap = await getDocs(q);
  return snap.docs.map(mapDocToReport);
}

export async function fetchReportFromFirestore(id) {
  const db = getFirestoreClient();
  if (!db) return null;
  const docRef = doc(db, 'reports', id);
  const snap = await getDoc(docRef);
  if (!snap.exists()) return null;
  return mapDocToReport(snap);
}

export function subscribeToReportsFromFirestore(onReports, onError) {
  const db = getFirestoreClient();
  if (!db) {
    onError?.(new Error('Firestore is not available'));
    return () => {};
  }

  const coll = collection(db, 'reports');
  const q = query(coll, orderBy('createdAt', 'desc'));

  return onSnapshot(
    q,
    (snapshot) => {
      onReports(snapshot.docs.map(mapDocToReport));
    },
    (error) => {
      console.error('Firestore subscription error', error);
      onError?.(error);
    }
  );
}

export function isFirebaseAvailable() {
  return !!getFirestoreClient();
}

export default {
  isFirebaseAvailable,
  fetchReportsFromFirestore,
  fetchReportFromFirestore,
  subscribeToReportsFromFirestore,
};
