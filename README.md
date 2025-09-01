# 🏥 AI Conversational Appointment Scheduling System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated AI-powered medical appointment scheduling system featuring a conversational interface, master-worker agent architecture, and secure patient ID management. Built with FastAPI, OpenAI GPT, and modern web technologies.

## ✨ Key Features

### 🤖 AI-Powered Conversational Interface
- **Natural Language Processing**: Book appointments using plain English ("Book me with Dr. Smith next Thursday at 3 PM")
- **Intelligent Intent Recognition**: Automatically detects booking, rescheduling, cancellation, and query intents
- **Context-Aware Conversations**: Maintains conversation memory across sessions
- **Smart Date/Time Parsing**: Handles relative dates ("tomorrow", "next Friday") and flexible time formats

### 🏗️ Advanced Architecture
- **Master-Worker Pattern**: Single master agent handles all user communication while worker agents process tasks
- **Conversation Memory**: Persistent session management with context preservation
- **Modular Design**: Separate agents for scheduling, queries, and appointment management
- **Scalable Backend**: FastAPI with async support and automatic API documentation

### 🔒 Security & Data Management
- **Unique Patient IDs**: Alphanumeric patient identification system (format: P + 2 letters + 4 numbers)
- **Secure Authentication**: Patient ID-based appointment access (no appointments without valid patient ID)
- **Data Persistence**: JSON-based storage with automatic backup and recovery
- **Privacy Protection**: Patient IDs not displayed in public interfaces

### 💻 Modern User Experience
- **Responsive Web Interface**: Mobile-friendly design with modern CSS
- **Registration System**: Streamlined patient registration with auto-redirect
- **Real-time Feedback**: Live countdown timers and status updates
- **Interactive Elements**: Clickable patient IDs for easy copying
- **Error Handling**: Comprehensive validation and user-friendly error messages

## 🚀 Live Demo

Experience the system in action:
1. **Registration**: `/register` - Create a new patient account
2. **AI Chat**: `/chat` - Natural language appointment booking
3. **Dashboard**: `/` - View system overview and statistics

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (GPT-3.5-turbo)
- Modern web browser

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-appointment-scheduler.git
cd ai-appointment-scheduler
```

### 2. Install Dependencies
```bash
pip install -r requirements_fastapi.txt
```

### 3. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# Required:
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for email reminders):
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

DEBUG=True
```

### 4. Run the Application
```bash
python main_improved.py
```

Visit `http://localhost:8000` to access the application.

## 🏗️ System Architecture

### Master-Worker Agent Pattern
```
User Request → Master Agent → Worker Agents → Data Store
                    ↓              ↓
              Conversation    [Scheduling, Query,
                Memory         Management Workers]
```

### Core Components

#### 🎯 Master Agent (`agents/master_agent.py`)
- Handles ALL user communication
- Manages conversation memory and context
- Coordinates with worker agents internally
- Provides natural language responses

#### ⚙️ Worker Agents
- **Scheduling Worker**: Processes appointment bookings
- **Query Worker**: Handles availability checks and searches  
- **Management Worker**: Manages rescheduling and cancellations

#### 💾 Data Store (`data_store.py`)
- Persistent JSON-based storage
- Automatic backup and recovery
- Patient ID management and uniqueness
- Appointment lifecycle management

## 🎮 Usage Examples

### Natural Language Appointment Booking
```
User: "Hi, I need to see Dr. Adams next Monday at 2 PM"
Assistant: "I'd be happy to help you book that appointment! I need your patient ID to proceed. Your patient ID is a 7-character code that starts with 'P' followed by letters and numbers (like PVY3830). What's your patient ID?"

User: "My patient ID is PQA8758"
Assistant: "Perfect! I've successfully booked your appointment. Sarthak Mishra is scheduled with Dr. Adams on Monday, September 2nd, 2025 at 02:00 PM."
```

### Appointment Management
```
User: "I need to reschedule my appointment to Friday morning"
System: Automatically identifies the patient's existing appointment and reschedules it

User: "What doctors are available this week?"
System: Provides real-time availability information
```

## 🔧 API Endpoints

### Core Endpoints
- `POST /api/chat` - AI conversational interface
- `POST /api/patients` - Patient registration
- `GET /api/appointments` - Appointment management
- `GET /api/doctors` - Doctor information

### System Endpoints
- `GET /api/stats` - System statistics
- `GET /api/health` - Health check
- `POST /api/cleanup` - Data maintenance

## 🏥 Sample Data

### Pre-configured Doctors
- **Dr. Adams** - General Medicine
- **Dr. Baker** - Pediatrics
- **Dr. Clark** - Dermatology  
- **Dr. Davis** - Endocrinology

### Patient ID Format
- **Format**: `P` + 2 uppercase letters + 4 digits
- **Examples**: `PQA8758`, `PWJ0123`, `PHC2040`
- **Uniqueness**: Guaranteed unique across all registrations

## 🔍 Advanced Features

### Conversation Memory
- Persistent session management
- Context preservation across interactions
- Smart information gathering for incomplete requests

### Automatic Cleanup
- Background task removes expired appointments
- Data integrity maintenance
- Configurable cleanup intervals

### Error Recovery
- Graceful handling of API failures
- Automatic retry mechanisms  
- User-friendly error messages

## 🛡️ Security Features

### Patient ID System
- Secure alphanumeric identification
- No appointments without valid patient ID
- Privacy protection in public interfaces

### Data Protection
- Automatic data backups
- Error recovery mechanisms
- Secure patient information handling

## 🎨 User Interface

### Registration Flow
1. Patient fills registration form
2. Receives unique patient ID with prominent display
3. 20-second countdown with auto-redirect
4. Clickable ID for easy copying

### Chat Interface  
- Clean, modern design
- Real-time message processing
- Mobile-responsive layout
- Conversation history

## 📊 Monitoring & Analytics

### System Statistics
- Patient and appointment counts
- Conversation memory usage
- System health metrics
- Data storage information

### Background Processes
- Automatic expired appointment cleanup
- Data backup creation
- System health monitoring

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_api_key

# Optional  
SENDER_EMAIL=email@domain.com
SENDER_PASSWORD=app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
DEBUG=True
```

### System Settings
- Cleanup interval: 6 hours (configurable)
- Session timeout: Configurable
- Maximum conversation history: Configurable

## 📈 Performance

### Optimizations
- Async FastAPI backend
- Efficient JSON data storage
- Memory-conscious conversation management
- Background task processing

### Scalability
- Modular architecture for easy scaling
- Stateless worker agents
- Configurable resource limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Future Enhancements

### Planned Features
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Multi-tenant clinic support
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] SMS notifications
- [ ] Advanced scheduling rules
- [ ] Analytics dashboard
- [ ] Mobile app development

### Technical Improvements
- [ ] Redis for session storage
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Automated testing suite
- [ ] Performance monitoring
- [ ] Load balancing support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing GPT-3.5-turbo API
- FastAPI community for excellent documentation
- Healthcare professionals for domain insights

## 📞 Support

For support, please open an issue on GitHub or contact:
- Email: dps.sarthak@gmail.com
- LinkedIn: https://www.linkedin.com/in/sarthakpattnaik/
- Twitter: @Sarthakpattna1

---

**Built with ❤️ using Python, FastAPI, and OpenAI GPT-3.5-turbo**