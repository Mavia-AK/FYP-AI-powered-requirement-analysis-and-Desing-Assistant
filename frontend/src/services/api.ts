const API_BASE_URL = 'http://localhost:8000/api';

export type AnalysisSummary = {
  'Total Requirements': number;
  'Valid Requirements': number;
  'Invalid Requirements': number;
  'Clear Requirements'?: number;
  'Ambiguous Requirements'?: number;
  'Average RQI Score'?: number;
  'Functional (FR)'?: number;
  'Non-Functional (NFR)'?: number;
}

export type AnalysisResultItem = {
  '#': number;
  'Requirement': string;
  'Validity': string;
  'Val. Score': string;
  'Val. Reason': string;
  'Ambiguity'?: string;
  'Amb. Score'?: string;
  'RQI Score'?: number;
  'Reason'?: string;
  'Type'?: string;
  'Type Score'?: string;
  'P(FR)'?: string;
  'P(NFR)'?: string;
}

export type UMLData = {
  png_base64?: string;
  [key: string]: any;
}

export type AnalysisResponse = {
  results: AnalysisResultItem[];
  summary: AnalysisSummary;
  uml_data?: UMLData;
}

export const analyzeText = async (text: string, modules: string[]): Promise<AnalysisResponse> => {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      requirements_text: text,
      modules,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Analysis failed');
  }

  return response.json();
};

export const uploadFile = async (file: File, modules: string[]): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('modules', modules.join(','));

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Upload failed');
  }

  return response.json();
};
