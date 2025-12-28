#!/usr/bin/env python3
"""
Seed script to create fake test accounts for development testing.
Run with: python seed_test_data.py
"""

from datetime import datetime, date
from app import create_app, db
from app.models import User, Profile, Photo, Like, Match

app = create_app()

# Test users data
TEST_USERS = [
    {
        "email": "maria.popescu@test.com",
        "password": "Test123!",
        "profile": {
            "first_name": "Maria",
            "last_name": "Popescu",
            "gender": "female",
            "date_of_birth": date(1995, 3, 15),
            "city": "Chicago",
            "state_province": "IL",
            "country": "USA",
            "denomination": "orthodox",
            "church_name": "St. George Romanian Orthodox Church",
            "church_attendance": "weekly",
            "faith_importance": "very_important",
            "speaks_romanian": "fluent",
            "romanian_origin_region": "transylvania",
            "years_in_north_america": "10_plus",
            "bio": "Bună! I'm Maria, a software engineer living in Chicago. I grew up in Cluj-Napoca and moved to the US for university. I'm actively involved in my church community and love our Romanian traditions. Looking for someone who shares my faith and values family as much as I do. I enjoy cooking mămăligă, hiking, and reading. 📚✝️",
            "occupation": "Software Engineer",
            "education": "masters",
            "height_cm": 165,
            "relationship_goal": "marriage",
            "looking_for_gender": "male",
            "looking_for_age_min": 27,
            "looking_for_age_max": 38,
            "conservatism_level": "traditional",
            "head_covering": "batic_at_church",
            "fasting_practice": "most_periods",
            "prayer_frequency": "daily",
            "bible_reading": "weekly",
            "family_role_view": "complementarian",
            "wants_spouse_same_denomination": True,
            "wants_church_wedding": True,
            "willing_to_relocate": True,
            "wants_children": "yes",
            "smoking": "never",
            "drinking": "occasionally",
        },
        "photos": [
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=500&fit=crop",
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=500&fit=crop",
        ]
    },
    {
        "email": "andrei.ionescu@test.com",
        "password": "Test123!",
        "profile": {
            "first_name": "Andrei",
            "last_name": "Ionescu",
            "gender": "male",
            "date_of_birth": date(1992, 7, 22),
            "city": "Toronto",
            "state_province": "ON",
            "country": "Canada",
            "denomination": "orthodox",
            "church_name": "Holy Trinity Romanian Orthodox Church",
            "church_attendance": "weekly",
            "faith_importance": "very_important",
            "speaks_romanian": "fluent",
            "romanian_origin_region": "bucharest",
            "years_in_north_america": "5_10",
            "bio": "Salut! I'm Andrei, a civil engineer from Bucharest now living in Toronto. Faith and family are the most important things in my life. I serve as a cantor at my church and love our beautiful Orthodox traditions. In my free time, I enjoy playing soccer, photography, and exploring the great outdoors. Looking for a kind, faithful woman to build a family with. 🇷🇴⛪",
            "occupation": "Civil Engineer",
            "education": "bachelors",
            "height_cm": 182,
            "relationship_goal": "marriage",
            "looking_for_gender": "female",
            "looking_for_age_min": 24,
            "looking_for_age_max": 32,
            "conservatism_level": "traditional",
            "fasting_practice": "strict_all_periods",
            "prayer_frequency": "multiple_daily",
            "bible_reading": "daily",
            "family_role_view": "traditional",
            "wants_spouse_same_denomination": True,
            "wants_church_wedding": True,
            "willing_to_relocate": True,
            "wants_children": "yes",
            "smoking": "never",
            "drinking": "rarely",
        },
        "photos": [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop",
            "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=500&fit=crop",
        ]
    },
    {
        "email": "elena.stanescu@test.com",
        "password": "Test123!",
        "profile": {
            "first_name": "Elena",
            "last_name": "Stănescu",
            "gender": "female",
            "date_of_birth": date(1997, 11, 8),
            "city": "Los Angeles",
            "state_province": "CA",
            "country": "USA",
            "denomination": "pentecostal",
            "church_name": "Romanian Pentecostal Church of LA",
            "church_attendance": "multiple_weekly",
            "faith_importance": "very_important",
            "speaks_romanian": "fluent",
            "romanian_origin_region": "moldova",
            "years_in_north_america": "0_5",
            "bio": "Hello! I'm Elena, a nurse who recently moved from Iași to Los Angeles. My faith in Jesus is everything to me - I love worshipping, praying, and being part of my church community. I'm looking for a godly man who loves the Lord and wants to serve Him together. I enjoy singing, volunteering, and spending time with family. God bless! 🙏💕",
            "occupation": "Registered Nurse",
            "education": "bachelors",
            "height_cm": 168,
            "relationship_goal": "marriage",
            "looking_for_gender": "male",
            "looking_for_age_min": 25,
            "looking_for_age_max": 35,
            "conservatism_level": "very_traditional",
            "head_covering": "pamblica",
            "fasting_practice": "some_holidays",
            "prayer_frequency": "multiple_daily",
            "bible_reading": "daily",
            "family_role_view": "traditional",
            "wants_spouse_same_denomination": True,
            "wants_church_wedding": True,
            "willing_to_relocate": False,
            "wants_children": "yes",
            "smoking": "never",
            "drinking": "never",
        },
        "photos": [
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop",
            "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=500&fit=crop",
        ]
    },
    {
        "email": "daniel.tudor@test.com",
        "password": "Test123!",
        "profile": {
            "first_name": "Daniel",
            "last_name": "Tudor",
            "gender": "male",
            "date_of_birth": date(1990, 5, 3),
            "city": "New York",
            "state_province": "NY",
            "country": "USA",
            "denomination": "baptist",
            "church_name": "First Romanian Baptist Church NYC",
            "church_attendance": "weekly",
            "faith_importance": "very_important",
            "speaks_romanian": "heritage",
            "romanian_origin_region": "banat",
            "years_in_north_america": "born_here",
            "bio": "Hi there! I'm Daniel, a second-generation Romanian-American working as a financial analyst in NYC. Though I was born here, my parents made sure I grew up with Romanian culture and Baptist faith. I'm looking for someone who values both our heritage and our faith. I enjoy playing guitar at church, cooking (yes, I make a mean sarmale!), and exploring the city. 🎸🗽",
            "occupation": "Financial Analyst",
            "education": "masters",
            "height_cm": 178,
            "relationship_goal": "marriage",
            "looking_for_gender": "female",
            "looking_for_age_min": 25,
            "looking_for_age_max": 35,
            "conservatism_level": "moderate",
            "fasting_practice": "rarely",
            "prayer_frequency": "daily",
            "bible_reading": "weekly",
            "family_role_view": "complementarian",
            "wants_spouse_same_denomination": False,
            "wants_church_wedding": True,
            "willing_to_relocate": False,
            "wants_children": "yes",
            "smoking": "never",
            "drinking": "socially",
        },
        "photos": [
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop",
            "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=500&fit=crop",
        ]
    }
]


def clear_test_data():
    """Remove existing test users"""
    test_emails = [u["email"] for u in TEST_USERS]
    for email in test_emails:
        user = User.query.filter_by(email=email).first()
        if user:
            # Delete related data
            Like.query.filter((Like.liker_id == user.id) | (Like.liked_id == user.id)).delete()
            Match.query.filter((Match.user1_id == user.id) | (Match.user2_id == user.id)).delete()
            Photo.query.filter_by(user_id=user.id).delete()
            Profile.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
    db.session.commit()
    print("✓ Cleared existing test data")


def create_test_users():
    """Create test users with profiles and photos"""
    created_users = []
    
    for user_data in TEST_USERS:
        # Create user
        user = User(email=user_data["email"])
        user.set_password(user_data["password"])
        user.is_verified = True
        user.email_verified = True
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create profile
        profile_data = user_data["profile"]
        profile = Profile(user_id=user.id)
        
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        db.session.add(profile)
        
        # Create photos
        for i, photo_url in enumerate(user_data["photos"]):
            photo = Photo(
                user_id=user.id,
                filename=f"test_photo_{user.id}_{i}.jpg",
                url=photo_url,
                is_primary=(i == 0),
                display_order=i
            )
            db.session.add(photo)
        
        created_users.append(user)
        print(f"✓ Created user: {user_data['profile']['first_name']} {user_data['profile']['last_name']} ({user_data['email']})")
    
    db.session.commit()
    return created_users


def create_test_interactions(users):
    """Create some likes and matches for testing"""
    # users[0] = Maria (F), users[1] = Andrei (M), users[2] = Elena (F), users[3] = Daniel (M)
    
    # Andrei likes Maria -> mutual like = match
    like1 = Like(liker_id=users[1].id, liked_id=users[0].id)
    db.session.add(like1)
    
    like2 = Like(liker_id=users[0].id, liked_id=users[1].id)
    db.session.add(like2)
    
    # Create match between Maria and Andrei
    match1 = Match(user1_id=users[0].id, user2_id=users[1].id, is_active=True)
    db.session.add(match1)
    print("✓ Created match: Maria ↔ Andrei")
    
    # Daniel likes Elena (pending - she hasn't liked back yet)
    like3 = Like(liker_id=users[3].id, liked_id=users[2].id)
    db.session.add(like3)
    print("✓ Created pending like: Daniel → Elena")
    
    # Daniel likes Maria (pending)
    like4 = Like(liker_id=users[3].id, liked_id=users[0].id)
    db.session.add(like4)
    print("✓ Created pending like: Daniel → Maria")
    
    db.session.commit()


def main():
    with app.app_context():
        print("\n🌱 Seeding test data...\n")
        
        # Clear any existing test data
        clear_test_data()
        
        # Create users
        users = create_test_users()
        
        # Create interactions
        create_test_interactions(users)
        
        print("\n" + "="*50)
        print("✅ Test data seeded successfully!")
        print("="*50)
        print("\n📧 Test Accounts (all passwords: Test123!):")
        print("-" * 50)
        for user_data in TEST_USERS:
            profile = user_data["profile"]
            print(f"  • {profile['first_name']} {profile['last_name']}")
            print(f"    Email: {user_data['email']}")
            print(f"    Gender: {profile['gender'].capitalize()}, {profile['denomination'].capitalize()}")
            print(f"    Location: {profile['city']}, {profile['state_province']}")
            print()
        
        print("🔗 Test Interactions:")
        print("-" * 50)
        print("  • Maria ↔ Andrei: MATCHED (can message each other)")
        print("  • Daniel → Elena: PENDING (Elena sees Daniel in 'Likes You')")
        print("  • Daniel → Maria: PENDING (Maria sees Daniel in 'Likes You')")
        print()
        print("💡 Login as Maria to see: 1 match + 1 pending like")
        print("💡 Login as Andrei to see: 1 match")
        print("💡 Login as Elena to see: 1 pending like")
        print("💡 Login as Daniel to see: 0 matches (his likes are pending)")
        print()


if __name__ == "__main__":
    main()

