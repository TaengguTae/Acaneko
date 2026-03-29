/**
 * API服务
 * 封装所有后端API调用
 */

const API_BASE_URL = 'http://localhost:8000/api'

export interface VectorModel {
  value: string
  label: string
}

export interface Language {
  value: string
  label: string
}

export interface DocumentInfo {
  id: string
  name: string
  size: number
  uploadTime: string
  status: 'pending' | 'parsing' | 'completed' | 'failed'
  chunks: number
}

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  documentCount: number
  createdAt: string
  status: 'active' | 'inactive'
  chunkSize: number
  overlapSize: number
  vectorModel: string
  language: string
}

export interface CreateKnowledgeBaseRequest {
  name: string
  description: string
  chunkSize: number
  overlapSize: number
  vectorModel: string
  language: string
}

export interface ParseStatusResponse {
  knowledgeBaseId: string
  totalDocuments: number
  completed: number
  failed: number
  inProgress: number
  percentage: number
}

class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Request failed')
    }

    return response.json()
  }

  async getVectorModels(): Promise<VectorModel[]> {
    return this.request<VectorModel[]>('/vector-models')
  }

  async getLanguages(): Promise<Language[]> {
    return this.request<Language[]>('/languages')
  }

  async getKnowledgeBases(): Promise<KnowledgeBase[]> {
    return this.request<KnowledgeBase[]>('/knowledge-bases')
  }

  async getKnowledgeBase(id: string): Promise<KnowledgeBase> {
    return this.request<KnowledgeBase>(`/knowledge-bases/${id}`)
  }

  private toSnakeCase(obj: any): any {
    if (obj === null || typeof obj !== 'object') {
      return obj
    }
    
    if (Array.isArray(obj)) {
      return obj.map(item => this.toSnakeCase(item))
    }
    
    const result: any = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
        result[snakeKey] = this.toSnakeCase(obj[key])
      }
    }
    return result
  }

  async createKnowledgeBase(data: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    return this.request<KnowledgeBase>('/knowledge-bases', {
      method: 'POST',
      body: JSON.stringify(this.toSnakeCase(data)),
    })
  }

  async updateKnowledgeBase(
    id: string,
    data: Partial<KnowledgeBase>
  ): Promise<KnowledgeBase> {
    return this.request<KnowledgeBase>(`/knowledge-bases/${id}`, {
      method: 'PUT',
      body: JSON.stringify(this.toSnakeCase(data)),
    })
  }

  async deleteKnowledgeBase(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/knowledge-bases/${id}`, {
      method: 'DELETE',
    })
  }

  async getDocuments(knowledgeBaseId: string): Promise<DocumentInfo[]> {
    return this.request<DocumentInfo[]>(`/knowledge-bases/${knowledgeBaseId}/documents`)
  }

  async uploadDocuments(
    knowledgeBaseId: string,
    files: File[]
  ): Promise<{ message: string; documents: DocumentInfo[] }> {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await fetch(
      `${this.baseUrl}/knowledge-bases/${knowledgeBaseId}/documents/upload`,
      {
        method: 'POST',
        body: formData,
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Upload failed')
    }

    return response.json()
  }

  async deleteDocument(
    knowledgeBaseId: string,
    documentId: string
  ): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/knowledge-bases/${knowledgeBaseId}/documents/${documentId}`,
      {
        method: 'DELETE',
      }
    )
  }

  async batchDeleteDocuments(
    knowledgeBaseId: string,
    documentIds: string[]
  ): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/knowledge-bases/${knowledgeBaseId}/documents/batch-delete`,
      {
        method: 'POST',
        body: JSON.stringify({ doc_ids: documentIds }),
      }
    )
  }

  async parseDocuments(
    knowledgeBaseId: string,
    chunkSize: number,
    overlapSize: number,
    vectorModel: string,
    language: string
  ): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/knowledge-bases/${knowledgeBaseId}/parse`,
      {
        method: 'POST',
        body: JSON.stringify({
          knowledge_base_id: knowledgeBaseId,
          chunk_size: chunkSize,
          overlap_size: overlapSize,
          vector_model: vectorModel,
          language: language,
        }),
      }
    )
  }

  async getParseStatus(knowledgeBaseId: string): Promise<ParseStatusResponse> {
    return this.request<ParseStatusResponse>(
      `/knowledge-bases/${knowledgeBaseId}/parse-status`
    )
  }
}

export const apiService = new ApiService()
