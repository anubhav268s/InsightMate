import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ChatRequest {
  message: string;
  mode: 'general' | 'personalized';
}

export interface ChatResponse {
  response: string;
  mode: string;
}

export interface UploadResponse {
  message: string;
  filename: string;
}

export interface UserData {
  files: any[];
  portfolio_links: any[];
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8001';

  constructor(private http: HttpClient) {}

  // Chat endpoints
  chatGeneral(message: string): Observable<ChatResponse> {
    const payload: ChatRequest = { message, mode: 'general' };
    return this.http.post<ChatResponse>(`${this.baseUrl}/api/chat`, payload);
  }

  chatPersonalized(message: string): Observable<ChatResponse> {
    const payload: ChatRequest = { message, mode: 'personalized' };
    return this.http.post<ChatResponse>(`${this.baseUrl}/api/chat`, payload);
  }

  // File upload
  uploadFile(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${this.baseUrl}/api/upload`, formData);
  }

  // Portfolio links
  addPortfolioLink(url: string, type: string = 'website'): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/portfolio-links`, { url, type });
  }

  // User data
  getUserData(): Observable<UserData> {
    return this.http.get<UserData>(`${this.baseUrl}/api/user-data`);
  }

  // Health check
  healthCheck(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/health`);
  }
}