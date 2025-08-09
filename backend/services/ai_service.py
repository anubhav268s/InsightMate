import openai
import os
from typing import Dict, Any, List
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class AIService:
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        # Default system prompts
        self.general_system_prompt = (
            "You are Insightmate, a helpful AI assistant. You can help with:\n"
            "- General questions and conversation\n"
            "- Programming and coding help\n"
            "- Writing assistance\n"
            "- Productivity tips\n"
            "- Technical explanations\n"
            "Be friendly, helpful, and concise in your responses."
        )
        self.personalized_system_prompt = (
            "You are Insightmate, a personalized AI assistant with access to the user's portfolio, resume, and personal data. "
            "Use this information to provide context-aware, personalized responses about:\n"
            "- Career advice based on their background\n"
            "- Resume feedback and improvements\n"
            "- Job application guidance\n"
            "- Portfolio analysis\n"
            "- Professional development suggestions\n"
            "Always reference specific details from their data when relevant.\n"
            "Be encouraging and provide actionable advice."
        )

    async def general_chat(self, message: str) -> str:
        """Handle general AI chat without personalization"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.general_system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback response if OpenAI API is not available
            return self._fallback_response(message, "general")

    async def personalized_chat(self, message: str, user_data: Dict[str, Any]) -> str:
        """Handle personalized chat using user's data"""
        try:
            # Build context from user data
            context = self._build_user_context(user_data)
            # Create personalized system prompt with context
            personalized_prompt = f"{self.personalized_system_prompt}\n\nUser Context:\n{context}"
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": personalized_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback response if OpenAI API is not available
            return self._fallback_response(message, "personalized", user_data)

    def _build_user_context(self, user_data: Dict[str, Any]) -> str:
        """Build context string from user data"""
        context_parts = []
        # Add portfolio links context
        if user_data.get("portfolio_links"):
            context_parts.append("Portfolio Links:")
            for link in user_data["portfolio_links"]:
                context_parts.append(f" - {link.get('type', 'website')}: {link.get('url', '')}")
                if link.get("content"):
                    # Add summarized content
                    context_parts.append(f"   Content summary: {link['content'][:200]}...")
        # Add uploaded files context
        if user_data.get("files"):
            context_parts.append("\nUploaded Files:")
            for filename, file_data in user_data["files"].items():
                context_parts.append(f" - {filename}")
                if file_data.get("content"):
                    # Add summarized content
                    context_parts.append(f"   Content: {file_data['content'][:300]}...")
        return "\n".join(context_parts) if context_parts else "No user data available."

    def _fallback_response(self, message: str, mode: str, user_data: Dict[str, Any] = None) -> str:
        """Provide fallback responses when OpenAI API is not available"""
        if mode == "general":
            return (
                f"I understand you're asking: \"{message}\"\n"
                "I'm currently running in fallback mode. Here are some ways I can help:\n"
                "- Answer general questions about programming, career advice, and productivity\n"
                "- Help with writing and communication\n"
                "- Provide technical explanations\n"
                "- Assist with project planning\n"
                "Please note: To get full AI-powered responses, make sure to set up your OpenAI API key in the environment variables."
            )
        else:
            user_info = ""
            if user_data:
                if user_data.get("portfolio_links"):
                    user_info += f"I can see you have {len(user_data['portfolio_links'])} portfolio links. "
                if user_data.get("files"):
                    user_info += f"You've uploaded {len(user_data['files'])} files. "
            return (
                f"I understand you're asking: \"{message}\"\n"
                f"{user_info}I'm currently running in fallback mode, but I can still help with:\n"
                "- General career advice based on your uploaded information\n"
                "- Resume and portfolio feedback\n"
                "- Job application guidance\n"
                "- Professional development suggestions\n"
                "To get personalized AI-powered insights, please set up your OpenAI API key."
            )

    def get_system_prompts(self) -> Dict[str, str]:
        """Get current system prompts for debugging"""
        return {
            "general": self.general_system_prompt,
            "personalized": self.personalized_system_prompt
        }