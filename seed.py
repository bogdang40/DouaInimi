"""Seed script to populate the database with test data."""
from datetime import date, timedelta
import random
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile
from app.models.photo import Photo

app = create_app()

# Sample data
FIRST_NAMES_MALE = ['Andrei', 'Alexandru', 'Stefan', 'Mihai', 'Ion', 'Cristian', 'Daniel', 'Gabriel', 'Adrian', 'Florin']
FIRST_NAMES_FEMALE = ['Maria', 'Elena', 'Ana', 'Ioana', 'Andreea', 'Cristina', 'Alexandra', 'Diana', 'Raluca', 'Simona']
LAST_NAMES = ['Popescu', 'Ionescu', 'Popa', 'Stan', 'Dumitru', 'Stoica', 'Constantin', 'Barbu', 'Nicolae', 'Marin']

CITIES_US = [
    ('Chicago', 'IL'), ('Los Angeles', 'CA'), ('New York', 'NY'), ('Detroit', 'MI'),
    ('Cleveland', 'OH'), ('Phoenix', 'AZ'), ('Houston', 'TX'), ('Philadelphia', 'PA'),
]
CITIES_CA = [
    ('Toronto', 'ON'), ('Montreal', 'QC'), ('Vancouver', 'BC'), ('Calgary', 'AB'),
]

DENOMINATIONS = ['orthodox', 'greek_catholic', 'baptist', 'pentecostal', 'evangelical']
ROMANIAN_REGIONS = ['transilvania', 'moldova', 'muntenia', 'banat', 'bucovina']
SPEAKS_ROMANIAN = ['fluent', 'conversational', 'heritage']
CHURCH_ATTENDANCE = ['weekly', 'monthly', 'holidays']
RELATIONSHIP_GOALS = ['marriage', 'serious', 'friendship_first']

BIOS = [
    "I'm a passionate person who loves spending time with family and attending church. Looking for someone who shares my faith and values.",
    "Born in Romania, living in North America for several years now. I cherish our traditions and am looking for a partner to build a godly family with.",
    "Faith and family are the most important things in my life. I enjoy cooking traditional Romanian food and sharing it with loved ones.",
    "I'm an active member of my church community and love serving others. Seeking a like-minded partner for a Christ-centered relationship.",
    "Love hiking, reading, and spending quality time with friends from church. Looking for someone genuine who values faith and commitment.",
    "Originally from Romania, I've maintained my faith and traditions while building a life here. Ready to meet someone special.",
    "I believe in the power of prayer and the importance of a strong faith foundation in relationships. Let's grow together in Christ.",
    "Family-oriented person who enjoys both quiet evenings and community gatherings. Looking for my partner in life and faith.",
]


def create_test_users():
    """Create test users with profiles."""
    users_created = []
    
    # Create 20 test users (10 male, 10 female)
    for i in range(20):
        gender = 'male' if i < 10 else 'female'
        first_names = FIRST_NAMES_MALE if gender == 'male' else FIRST_NAMES_FEMALE
        
        email = f"test{i+1}@example.com"
        
        # Check if user already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"User {email} already exists, skipping...")
            continue
        
        user = User(email=email)
        user.set_password('Password123')
        user.is_verified = True
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        # Create profile
        first_name = random.choice(first_names)
        last_name = random.choice(LAST_NAMES)
        
        # Random age between 22 and 45
        age = random.randint(22, 45)
        dob = date.today() - timedelta(days=age*365 + random.randint(0, 364))
        
        # Random location
        if random.random() < 0.8:  # 80% US, 20% Canada
            city, state = random.choice(CITIES_US)
            country = 'US'
        else:
            city, state = random.choice(CITIES_CA)
            country = 'CA'
        
        profile = Profile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            gender=gender,
            city=city,
            state_province=state,
            country=country,
            romanian_origin_region=random.choice(ROMANIAN_REGIONS),
            speaks_romanian=random.choice(SPEAKS_ROMANIAN),
            years_in_north_america=random.randint(2, 25),
            denomination=random.choice(DENOMINATIONS),
            church_attendance=random.choice(CHURCH_ATTENDANCE),
            faith_importance='very_important',
            bio=random.choice(BIOS),
            occupation=random.choice(['Engineer', 'Teacher', 'Nurse', 'Business Owner', 'Accountant', 'Doctor', 'Designer']),
            education=random.choice(['bachelors', 'masters', 'high_school']),
            height_cm=random.randint(155, 195) if gender == 'male' else random.randint(150, 175),
            wants_children=random.choice(['yes', 'maybe']),
            smoking='never',
            drinking=random.choice(['never', 'socially']),
            looking_for_gender='female' if gender == 'male' else 'male',
            looking_for_age_min=max(18, age - 8),
            looking_for_age_max=min(99, age + 8),
            relationship_goal=random.choice(RELATIONSHIP_GOALS),
        )
        db.session.add(profile)
        
        users_created.append(user)
        print(f"Created user: {first_name} {last_name} ({email})")
    
    db.session.commit()
    print(f"\nCreated {len(users_created)} test users")
    return users_created


def main():
    """Main seed function."""
    with app.app_context():
        print("🌱 Seeding database...")
        print("-" * 40)
        
        # Create tables if they don't exist
        db.create_all()
        
        # Create test users
        create_test_users()
        
        print("-" * 40)
        print("✅ Database seeded successfully!")
        print("\nTest accounts:")
        print("  Email: test1@example.com - test20@example.com")
        print("  Password: Password123")


if __name__ == '__main__':
    main()

