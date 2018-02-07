PLANNED = 'planned'
AVAILABLE = 'available'
CANCELLED = 'cancelled'
SOLD_OUT = 'sold-out'
ARCHIVED = 'archived'

STATUS_CHOICES = (
    (PLANNED, PLANNED),
    (AVAILABLE, AVAILABLE),
    (CANCELLED, CANCELLED),
    (SOLD_OUT, SOLD_OUT),
    (ARCHIVED, ARCHIVED),
)

ADMIN = 'Administrator'
CITY_ADMIN = 'City Administrator'
TEACHER_CITY_ADMIN = 'Teacher(City Administrator)'
TEACHER = 'Teacher'
SITE_USER = 'Site user'
SITE_GUEST = 'Guest of the site'
