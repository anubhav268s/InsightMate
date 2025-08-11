import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  mode: 'general' | 'personalized';
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  public messages$ = this.messagesSubject.asObservable();

  private isLoadingSubject = new BehaviorSubject<boolean>(false);
  public isLoading$ = this.isLoadingSubject.asObservable();

  constructor() {}

  addMessage(message: ChatMessage): void {
    const currentMessages = this.messagesSubject.value;
    this.messagesSubject.next([...currentMessages, message]);
  }

  addUserMessage(text: string, mode: 'general' | 'personalized'): ChatMessage {
    const message: ChatMessage = {
      id: this.generateId(),
      text,
      isUser: true,
      timestamp: new Date(),
      mode
    };
    this.addMessage(message);
    return message;
  }

  addAiMessage(text: string, mode: 'general' | 'personalized'): ChatMessage {
    const message: ChatMessage = {
      id: this.generateId(),
      text,
      isUser: false,
      timestamp: new Date(),
      mode
    };
    this.addMessage(message);
    return message;
  }

  setLoading(loading: boolean): void {
    this.isLoadingSubject.next(loading);
  }

  clearMessages(): void {
    this.messagesSubject.next([]);
  }

  getMessages(): ChatMessage[] {
    return this.messagesSubject.value;
  }

  private generateId(): string {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  }
}