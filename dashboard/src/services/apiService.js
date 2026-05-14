import firebaseClient from './firebaseClient';

function formatIssueType(str) {
  if (!str) return 'Unknown';
  return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ');
}

function mapReportToIssue(report) {
  return {
    id: report.reportId,
    description: report.analysis?.description || '',
    impact: report.analysis?.impact || '',
    issueType: formatIssueType(report.analysis?.issueType),
    suggestedAction: report.analysis?.suggestedAction || '',
    urgency: (report.analysis?.urgency || 'medium').toLowerCase(),
    latitude: report.location?.latitude || 0,
    longitude: report.location?.longitude || 0,
    image: report.imageUrl || '',
    createdAt: report.createdAt || new Date().toISOString(),
    updatedAt: report.updatedAt || report.createdAt || new Date().toISOString()
  };
}

export const apiService = {
  async fetchReports() {
    const reports = await firebaseClient.fetchReportsFromFirestore();
    const mapped = (reports || []).map(mapReportToIssue);
    console.log('Fetched reports:', reports);
    console.log('Mapped issues:', mapped);
    return mapped;
  },

  async fetchReportById(id) {
    const report = await firebaseClient.fetchReportFromFirestore(id);
    if (!report) {
      throw new Error('Failed to fetch report from Firestore');
    }
    return mapReportToIssue(report);
  },
};

export default apiService;
