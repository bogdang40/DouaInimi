# 💕 Două Inimi

**Two Hearts, One Faith** — A dating platform for Romanian Christians of all denominations in the USA & Canada.

## ✨ Features

### For All Christian Denominations
- Orthodox, Catholic, Baptist, Pentecostal, Evangelical, and more
- Denomination-specific matching preferences
- Filter by same-denomination preference

### Romanian Heritage
- Romanian language proficiency levels
- Romanian regions of origin
- Cultural heritage preservation

### Traditional Values
- **Conservatism Level** - Very Traditional, Traditional, Moderate, Modern
- **Head Covering** (Women) - Batic, Pamblica, Church only, Sometimes, None
- **Fasting Practice** - Strict, Most periods, Some, Rarely, None
- **Prayer Frequency** - Multiple times daily, Daily, Weekly, Occasionally
- **Bible Reading** - Daily, Weekly, Monthly, Occasionally
- **Family Role Views** - Traditional, Complementarian, Egalitarian, Flexible
- **Church Wedding** preference

### Core Features
- User registration & authentication
- Profile creation with photos
- Discover & browse potential matches
- Like/Pass on profiles
- Mutual matching system
- Real-time messaging
- Report & block functionality

## 🛠 Tech Stack

- **Backend**: Flask 3.x, SQLAlchemy, Flask-Login
- **Frontend**: Jinja2 templates, Tailwind CSS, HTMX
- **Database**: PostgreSQL (SQLite for development)
- **Icons**: Lucide Icons
- **Fonts**: Cormorant Garamond, Inter

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/doua-inimi.git
cd doua-inimi
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
python run.py
```

Visit `http://localhost:5001` to see the app!

## 📁 Project Structure

```
Dating/
├── app/
│   ├── __init__.py         # App factory
│   ├── config.py           # Configuration
│   ├── extensions.py       # Flask extensions
│   ├── forms/              # WTForms
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # Blueprint routes
│   ├── static/             # CSS, JS, images
│   └── templates/          # Jinja2 templates
├── migrations/             # Database migrations
├── requirements.txt        # Python dependencies
├── run.py                  # Entry point
└── README.md
```

## 🎨 Design

The app features a dark theme with:
- Glassmorphism effects
- Rose-to-purple gradient accents
- Elegant Cormorant Garamond headings
- Clean Inter body text
- Smooth animations and transitions

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, email: support@douainimi.com

---

Made with 💕 for the Romanian Christian community in North America
