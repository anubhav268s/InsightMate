// import { Component, signal } from '@angular/core';

// @Component({
//   selector: 'app-root',
//   imports: [],
//   templateUrl: './app.html',
//   styleUrl: './app.scss'
// })
// export class App {
//   protected readonly title = signal('frontend');
// }

import { Component, OnInit, OnDestroy, AfterViewChecked, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ApiService } from './services/api.service';
import { ChatMessage, ChatService } from './services/chat.service';


@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App implements OnInit, OnDestroy, AfterViewChecked {
   @ViewChild('chatMessages') private chatMessagesContainer!: ElementRef;
  
  title = 'Insightmate';
  currentMode: 'general' | 'personalized' = 'general';
  sidebarVisible = false;
  messageText = '';
  messages: ChatMessage[] = [];
  isLoading = false;
  backendConnected = false;
  activeNavItem = 'chat'; // Track active navigation item

  private destroy$ = new Subject<void>();

  constructor(
    private apiService: ApiService,
    private chatService: ChatService
  ) {}

  ngOnInit() {
    // Subscribe to chat messages
    this.chatService.messages$
      .pipe(takeUntil(this.destroy$))
      .subscribe(messages => {
        this.messages = messages;
      });

    // Subscribe to loading state
    this.chatService.isLoading$
      .pipe(takeUntil(this.destroy$))
      .subscribe(loading => {
        this.isLoading = loading;
      });

    // Check backend connection
    this.checkBackendConnection();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  toggleSidebar() {
    this.sidebarVisible = !this.sidebarVisible;
  }

  switchMode(mode: 'general' | 'personalized') {
    this.currentMode = mode;
    // Optionally clear messages when switching modes
    // this.chatService.clearMessages();
  }

  // Navigation methods
  setActiveNav(navItem: string) {
    this.activeNavItem = navItem;
  }

  navigateToUpload() {
    this.setActiveNav('upload');
    this.triggerFileUpload();
  }

  navigateToPortfolio() {
    this.setActiveNav('portfolio');
    this.addPortfolioLink();
  }

  navigateToData() {
    this.setActiveNav('data');
    // Show user data summary
    this.apiService.getUserData()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          const fileCount = data.files ? data.files.length : 0;
          const linkCount = data.portfolio_links ? data.portfolio_links.length : 0;
          this.chatService.addAiMessage(
            `Your Data Summary:\n\n* **Files uploaded:** ${fileCount}\n* **Portfolio links:** ${linkCount}\n\nI can use this information to provide personalized assistance!`,
            'personalized'
          );
        },
        error: (error) => {
          console.error('Error fetching user data:', error);
          this.chatService.addAiMessage(
            "❌ Sorry, I couldn't retrieve your data at the moment. Please try again.",
            'personalized'
          );
        }
      });
  }

  navigateToChat() {
    this.setActiveNav('chat');
    this.startChat();
  }

  sendMessage() {
    if (this.messageText.trim()) {
      const userMessage = this.messageText.trim();
      // Add user message to chat
      this.chatService.addUserMessage(userMessage, this.currentMode);
      // Clear input
      this.messageText = '';
      // Set loading state
      this.chatService.setLoading(true);
      // Send to appropriate endpoint
      const apiCall = this.currentMode === 'general'
        ? this.apiService.chatGeneral(userMessage)
        : this.apiService.chatPersonalized(userMessage);
      apiCall
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (response) => {
            this.chatService.addAiMessage(response.response, this.currentMode);
            this.chatService.setLoading(false);
          },
          error: (error) => {
            console.error('Chat error:', error);
            const errorMessage = this.backendConnected
              ? 'Sorry, I encountered an error. Please try again.'
              : 'Backend server is not running. Please start the server first.';
            this.chatService.addAiMessage(errorMessage, this.currentMode);
            this.chatService.setLoading(false);
          }
        });
    }
  }

  // Trigger file upload
  triggerFileUpload() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf,.txt,.doc,.docx,.jpg,.jpeg,.png,.gif';
    fileInput.onchange = (event: any) => this.onFileUpload(event);
    fileInput.click();
  }

  // Handle file upload (to be implemented)
  onFileUpload(event: any) {
    // Implementation goes here
  }

  // Add portfolio link functionality
  addPortfolioLink() {
    const url = prompt('Enter your portfolio URL (LinkedIn, GitHub, personal website):');
    if (url && url.trim()) {
      this.chatService.setLoading(true);
      // Determine the type of link
      let type = 'website';
      if (url.includes('linkedin.com')) {
        type = 'linkedin';
      } else if (url.includes('github.com')) {
        type = 'github';
      }
      this.apiService.addPortfolioLink(url.trim(), type)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (response) => {
            console.log('Portfolio link added:', response);
            this.chatService.addAiMessage(
              `✅ Portfolio link added successfully! I can now reference your ${type} profile when providing personalized advice.`,
              'personalized'
            );
            this.chatService.setLoading(false);
          },
          error: (error) => {
            console.error('Portfolio link error:', error);
            this.chatService.addAiMessage(
              "❌ Sorry, there was an error adding your portfolio link. Please check the URL and try again.",
              'personalized'
            );
            this.chatService.setLoading(false);
          }
        });
    }
  }

  // Start chat functionality
  startChat() {
    // Focus on the message input
    const messageInput = document.querySelector('#messageInput') as HTMLInputElement;
    if (messageInput) {
      messageInput.focus();
      messageInput.placeholder = 'Ask me anything about your career, resume, or professional development...';
    }
  }

  private checkBackendConnection() {
    this.apiService.healthCheck()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.backendConnected = true;
          console.log('Backend connected successfully');
        },
        error: () => {
          this.backendConnected = false;
          console.log('Backend not connected');
        }
      });
  }
   

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

   scrollToBottom() {
    try {
      this.chatMessagesContainer.nativeElement.scrollTop = this.chatMessagesContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }

  // When adding a new message:
  addMessage(msg: any) {
    this.messages.push(msg); // Add to end
    // Angular will trigger ngAfterViewChecked and scroll automatically
  }
}