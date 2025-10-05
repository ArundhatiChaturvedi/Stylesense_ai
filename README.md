# 🎨 StyleSense AI - Samsung Prism GenAI Hackathon 2025

[![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactnative.dev/)
[![Expo](https://img.shields.io/badge/Expo-000020?style=for-the-badge&logo=expo&logoColor=white)](https://expo.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B6B?style=for-the-badge)](https://docs.trychroma.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1E88E5?style=for-the-badge&logo=chainlink&logoColor=white)](https://www.langchain.com/)

> **Your Personal AI Fashion Stylist** - Revolutionizing fashion recommendations through AI-powered wardrobe analysis, celebrity style matching, and weather-aware outfit suggestions.

## 🌟 Project Overview

**StyleSense AI** is an intelligent fashion recommendation system that combines computer vision, natural language processing, and vector databases to provide personalized style advice. Built for the Samsung Prism GenAI Hackathon 2025, it transforms how people interact with their wardrobes through AI-driven insights.

### 🎯 Core Features

- **📸 Smart Wardrobe Analysis**: Upload photos of your clothing items for AI-powered analysis
- **👗 Celebrity Style Matching**: Get matched with celebrity twins based on your fashion preferences
- **🌤️ Weather-Aware Recommendations**: Outfit suggestions adapted to current weather conditions
- **🛍️ Purchase Integration**: Import order history to build comprehensive style profiles
- **💬 Natural Language Queries**: Ask fashion questions in plain English
- **📱 Cross-Platform Mobile App**: Beautiful React Native interface with Expo

### 🏆 Hackathon Innovation

This project showcases cutting-edge GenAI applications in fashion technology:
- **Multi-modal AI**: Combines text and image analysis using Google Gemini
- **Vector Search**: Advanced semantic matching with ChromaDB
- **Real-time Processing**: Instant style recommendations with weather integration
- **Personalization**: Learns from user wardrobes and preferences
- **Scalable Architecture**: Production-ready backend with comprehensive API

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (3.8+)
- **Expo CLI**: `npm install -g @expo/cli`
- **Android Studio** or **iOS Simulator**
- **Google Gemini API Key**
- **Weather API Key** (optional)

### 🔧 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ArundhatiChaturvedi/Stylesense_ai.git
   cd Stylesense_ai
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   # Add your API keys to .env:
   # GEMINI_API_KEY=your_gemini_api_key_here
   # WEATHER_API_KEY=your_weather_api_key_here
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Start ChromaDB** (Required for vector database)
   ```bash
   pip install chromadb
   chroma run --host localhost --port 8000
   ```

### 🚀 Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   python main.py
   # Server runs on http://localhost:8080
   ```

2. **Start Mobile App**
   ```bash
   cd frontend
   npx expo start
   # Choose your platform: Android/iOS/Web
   ```

3. **Access the Application**
   - Scan QR code with Expo Go app (mobile)
   - Press 'a' for Android emulator
   - Press 'i' for iOS simulator
   - Press 'w' for web version

## 🏗️ Architecture

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  React Native   │◄──►│   FastAPI       │◄──►│   ChromaDB      │
│   Frontend      │    │   Backend       │    │  Vector Store   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Expo Router   │    │ Google Gemini   │    │   Sentence      │
│   Navigation    │    │   Vision API    │    │  Transformers   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🗂️ Project Structure
```
StyleSense_AI/
├── 📱 frontend/                 # React Native mobile app
│   ├── app/                     # Expo Router pages
│   │   ├── index.tsx           # Home screen
│   │   ├── screens/            # App screens
│   │   │   ├── model.tsx       # My Closet view
│   │   │   ├── profile.tsx     # User profile
│   │   │   └── recommend.tsx   # Recommendations
│   │   └── services/           # API services
│   │       └── api.ts          # Backend communication
│   ├── components/             # Reusable UI components
│   ├── contexts/               # React contexts
│   └── assets/                 # Images, fonts, etc.
│
├── 🔧 backend/                  # Python FastAPI server
│   ├── app/                    # Application modules
│   │   ├── api.py             # REST API endpoints
│   │   ├── recommender.py     # AI recommendation engine
│   │   ├── database.py        # ChromaDB operations
│   │   └── data_loader.py     # Dataset loading utilities
│   ├── main.py                # Server entry point
│   ├── requirements.txt       # Python dependencies
│   └── test_*.py             # Testing utilities
│
└── 📄 README.md               # This file
```

## 🔌 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/user/{user_id}/status` | User wardrobe status |
| `POST` | `/user/styles/upload-base64` | Upload wardrobe images |
| `POST` | `/user/styles/load-orders` | Import purchase history |
| `POST` | `/recommend` | Get style recommendations |
| `DELETE` | `/user/{user_id}/wardrobe` | Clear user wardrobe |

### Example API Usage

**Get Style Recommendation:**
```json
POST /recommend
{
  "user_id": "user123",
  "user_prompt": "I need a casual outfit for a coffee date",
  "current_location": "Mumbai"
}
```

**Response:**
```json
{
  "celebrity_twin": "Emma Stone",
  "weather_info": "The weather in Mumbai is 28°C with partly cloudy conditions",
  "final_recommendation": "Perfect weather for a light denim jacket...",
  "items_owned": [...],
  "items_to_buy": [...],
  "extracted_emotion": "romantic, casual"
}
```

## 🤖 AI Features

### 1. **Multi-Modal Analysis**
- **Image Processing**: Gemini Vision API analyzes clothing items
- **Text Understanding**: Natural language processing for user queries
- **Semantic Matching**: Vector embeddings for style similarity

### 2. **Smart Recommendations**
- **Weather Integration**: Real-time weather data influences suggestions
- **Celebrity Matching**: Style analysis against celebrity fashion database
- **Personal History**: Learns from user's wardrobe and purchases

### 3. **Vector Database**
- **ChromaDB Integration**: Efficient similarity search
- **Multiple Collections**: Separate stores for wardrobes, products, celebrities
- **Semantic Search**: Find items based on style descriptions

## 📱 Mobile App Features

### User Interface
- **Intuitive Design**: Clean, modern interface with smooth animations
- **Photo Upload**: Multi-image selection with progress tracking
- **Real-time Chat**: Natural language interaction with AI stylist
- **Weather Display**: Current conditions and outfit adaptation

### User Experience
- **Onboarding Flow**: Easy wardrobe setup process
- **Progress Tracking**: Visual feedback for uploads and processing
- **Cross-Platform**: Works on Android, iOS, and web
- **Offline Ready**: Core functionality available without internet

## 🛠️ Technical Implementation

### Backend Technologies
- **FastAPI**: High-performance async API framework
- **ChromaDB**: Vector database for similarity search
- **Google Gemini**: Multi-modal AI for image and text analysis
- **SentenceTransformers**: Text embedding generation
- **Weather API**: Real-time weather data integration

### Frontend Technologies
- **React Native**: Cross-platform mobile development
- **Expo**: Development platform and tools
- **TypeScript**: Type-safe JavaScript development
- **Expo Router**: File-based navigation system
- **AsyncStorage**: Local data persistence

### Development Tools
- **Hot Reload**: Instant development feedback
- **Type Safety**: Full TypeScript integration
- **API Testing**: Comprehensive test suites
- **Error Handling**: Robust error management
- **Performance Monitoring**: Built-in performance tracking

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python complete_sys_test.py    # Comprehensive system tests
python test_gemini_api.py      # Gemini API connectivity
python debug_celebrity.py     # Celebrity dataset analysis
```

### Test Coverage
- ✅ API Health Checks
- ✅ Database Connectivity
- ✅ Image Upload Processing
- ✅ Recommendation Generation
- ✅ User Wardrobe Management
- ✅ Weather Integration
- ✅ Vector Search Functionality

## 🚀 Deployment

### Production Checklist
- [ ] Set production API keys in `.env`
- [ ] Configure CORS for your domain
- [ ] Set up PostgreSQL for production database
- [ ] Deploy ChromaDB with persistent storage
- [ ] Build Expo app for app stores
- [ ] Set up monitoring and logging

### Environment Variables
```env
# Backend (.env)
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_api_key
MOCK_USER_ID=default_user
DEFAULT_LOCATION=Mumbai

# Optional: Database URLs, API endpoints, etc.
```

## 🤝 Contributing

This hackathon project welcomes contributions and feedback:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Commit changes**: `git commit -m 'Add some feature'`
4. **Push to branch**: `git push origin feature-name`
5. **Submit pull request**

## 🏆 Hackathon Highlights

### Innovation Points
- **Novel AI Integration**: Combines vision, language, and search AI
- **Real-world Application**: Solves genuine fashion discovery problems
- **Scalable Architecture**: Production-ready technical implementation
- **User-Centric Design**: Intuitive mobile-first experience
- **Advanced Features**: Weather integration, celebrity matching, semantic search

### Technical Excellence
- **Modern Stack**: Latest React Native, FastAPI, and AI technologies
- **Performance Optimized**: Efficient vector search and caching
- **Cross-Platform**: Single codebase for multiple platforms
- **Robust Testing**: Comprehensive test coverage
- **Documentation**: Detailed technical documentation

## 👥 Team

**Built for Samsung Prism GenAI Hackathon 2025**

- **Frontend Development**: React Native, Expo, TypeScript
- **Backend Development**: Python, FastAPI, AI Integration
- **AI/ML Engineering**: Google Gemini, ChromaDB, Vector Search
- **UI/UX Design**: Mobile-first design, user experience optimization

## 🎥 Demo Submission

### 📌 Video Demonstration
You can watch our project demo here:  
👉 [Demo Submission Link]([https://your-demo-link-here](https://drive.google.com/file/d/1F8FxTCRYTjptE-1BuUL6DIB1U_1TtIPK/view?usp=sharing))

## 📄 License

This project is created for the Samsung Prism GenAI Hackathon 2025. See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Samsung Prism**: For hosting this innovative hackathon
- **Google Gemini**: For powerful multi-modal AI capabilities
- **Expo Team**: For excellent mobile development tools
- **ChromaDB**: For efficient vector database solutions
- **FastAPI Community**: For the amazing async Python framework

---

**🌟 Experience the future of AI-powered fashion with StyleSense AI!**

*Built with ❤️ for Samsung Prism GenAI Hackathon 2025*
