import { createContext, useContext, useState } from 'react';

const LanguageContext = createContext();

const translations = {
  en: {
    // App
    appName: 'MedBook',
    appTagline: 'Book and manage your medical appointments, all in one place.',

    // Landing
    newHere: 'New here?',
    createAccount: 'Create an account',
    alreadyHaveAccount: 'Already have an account?',
    signIn: 'Sign in',
    or: 'or',
    featureEasy: 'Easy',
    featureEasyDesc: 'Book in seconds',
    featureSecure: 'Secure',
    featureSecureDesc: 'Your data is safe',
    featureFast: 'Fast',
    featureFastDesc: 'No waiting around',

    // Auth
    email: 'Email',
    password: 'Password',
    role: 'Role',
    client: 'Client',
    doctor: 'Doctor',
    signInTitle: 'Sign in to MedBook',
    backToHome: 'Back to Home',
    registerTitle: 'Create your account',
    fullName: 'Full Name',
    username: 'Username',
    specialization: 'Specialization',
    selectSpecialization: 'Select Specialization',
    register: 'Register',
    alreadyHaveAccountSignIn: 'Already have an account? Sign in',
    signOut: 'Sign out',

    // Validation
    emailRequired: 'Email is required',
    passwordRequired: 'Password is required',
    fullNameRequired: 'Full name is required',
    fullNameMin: 'Full name must be at least 2 characters',
    usernameRequired: 'Username is required',
    emailInvalid: 'Email format is invalid',
    passwordMin: 'Password must be at least 6 characters',
    passwordFormat: 'Password must contain both letters and numbers',
    specializationRequired: 'Specialization is required for doctors',
    errorOccurred: 'An error occurred.',

    // Dashboard
    dashboard: 'Dashboard',
    welcomeBack: 'Welcome back',
    manageAppointments: 'Manage your appointments',
    newAppointment: 'New Appointment',
    myAppointments: 'My Appointments',
    account: 'Account',

    // Appointments
    addAppointmentTitle: 'New Appointment',
    editAppointmentTitle: 'Edit Appointment',
    date: 'Date',
    from: 'From',
    to: 'To',
    selectDoctor: 'Select Doctor',
    comments: 'Comments',
    bookAppointment: 'Book Appointment',
    saveChanges: 'Save Changes',
    backToDashboard: 'Back to Dashboard',
    allFieldsRequired: 'All fields are required',

    // Show Appointments
    yourAppointments: 'Your Appointments',
    noAppointmentsYet: 'No appointments yet',
    noAppointmentsDesc: 'Head to the dashboard to book your first one.',
    past: 'Past',
    time: 'Time',
    notes: 'Notes',
    edit: 'Edit',
    delete: 'Delete',
    confirmDelete: 'Are you sure you want to delete this appointment?\n\nThis action cannot be undone.',
    confirmAccept: 'Accept this appointment?',
    confirmDecline: 'Are you sure you want to decline this appointment?\n\nThe client will be notified.',

    // Doctor view
    doctorAppointmentsTitle: "Your Clients' Appointments",
    noAppointmentsScheduled: 'No appointments scheduled',
    noAppointmentsScheduledDesc: 'Clients will book appointments with you as they become available.',
    clientName: 'Client',
    cancelAppointment: 'Cancel Appointment',
    acceptAppointment: 'Accept',
    declineAppointment: 'Decline',

    // Status
    status: 'Status',
    statusPending: 'Pending',
    statusConfirmed: 'Confirmed',
    statusDeclined: 'Declined',

    // Availability
    availability: 'Availability',
    availabilityTitle: 'Weekly Availability',
    availabilitySaved: 'Availability saved successfully',
    addTimeWindow: 'Add hours',
    remove: 'Remove',
    noSlotsAvailable: 'No available slots for this date',
    selectDoctorFirst: 'Select a doctor first',
    selectDateFirst: 'Select a date',
    monday: 'Monday',
    tuesday: 'Tuesday',
    wednesday: 'Wednesday',
    thursday: 'Thursday',
    friday: 'Friday',
    saturday: 'Saturday',
    sunday: 'Sunday',

    // Account
    accountTitle: 'Account',
    back: 'Back',
    failedToLoad: 'Failed to load account details',
    editProfile: 'Edit Profile',
    currentPassword: 'Current Password',
    newPassword: 'New Password',
    profileUpdated: 'Profile updated successfully',

    // Confirm / Toast
    cancelBtn: 'Cancel',
    confirmDeleteBtn: 'Delete',
  },
  el: {
    // App
    appName: 'MedBook',
    appTagline: 'Κλείστε και διαχειριστείτε τα ιατρικά σας ραντεβού, όλα σε ένα μέρος.',

    // Landing
    newHere: 'Νέος χρήστης;',
    createAccount: 'Δημιουργία λογαριασμού',
    alreadyHaveAccount: 'Έχετε ήδη λογαριασμό;',
    signIn: 'Σύνδεση',
    or: 'ή',
    featureEasy: 'Εύκολο',
    featureEasyDesc: 'Κλείστε σε δευτερόλεπτα',
    featureSecure: 'Ασφαλές',
    featureSecureDesc: 'Τα δεδομένα σας προστατεύονται',
    featureFast: 'Γρήγορο',
    featureFastDesc: 'Χωρίς αναμονή',

    // Auth
    email: 'Email',
    password: 'Κωδικός',
    role: 'Ρόλος',
    client: 'Πελάτης',
    doctor: 'Γιατρός',
    signInTitle: 'Σύνδεση στο MedBook',
    backToHome: 'Πίσω στην αρχική',
    registerTitle: 'Δημιουργία λογαριασμού',
    fullName: 'Ονοματεπώνυμο',
    username: 'Όνομα χρήστη',
    specialization: 'Ειδικότητα',
    selectSpecialization: 'Επιλέξτε ειδικότητα',
    register: 'Εγγραφή',
    alreadyHaveAccountSignIn: 'Έχετε ήδη λογαριασμό; Σύνδεση',
    signOut: 'Αποσύνδεση',

    // Validation
    emailRequired: 'Το email είναι υποχρεωτικό',
    passwordRequired: 'Ο κωδικός είναι υποχρεωτικός',
    fullNameRequired: 'Το ονοματεπώνυμο είναι υποχρεωτικό',
    fullNameMin: 'Το ονοματεπώνυμο πρέπει να έχει τουλάχιστον 2 χαρακτήρες',
    usernameRequired: 'Το όνομα χρήστη είναι υποχρεωτικό',
    emailInvalid: 'Μη έγκυρη μορφή email',
    passwordMin: 'Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες',
    passwordFormat: 'Ο κωδικός πρέπει να περιέχει γράμματα και αριθμούς',
    specializationRequired: 'Η ειδικότητα είναι υποχρεωτική για γιατρούς',
    errorOccurred: 'Παρουσιάστηκε σφάλμα.',

    // Dashboard
    dashboard: 'Πίνακας ελέγχου',
    welcomeBack: 'Καλώς ήρθατε',
    manageAppointments: 'Διαχειριστείτε τα ραντεβού σας',
    newAppointment: 'Νέο Ραντεβού',
    myAppointments: 'Τα Ραντεβού μου',
    account: 'Λογαριασμός',

    // Appointments
    addAppointmentTitle: 'Νέο Ραντεβού',
    editAppointmentTitle: 'Επεξεργασία Ραντεβού',
    date: 'Ημερομηνία',
    from: 'Από',
    to: 'Έως',
    selectDoctor: 'Επιλέξτε γιατρό',
    comments: 'Σχόλια',
    bookAppointment: 'Κλείσιμο Ραντεβού',
    saveChanges: 'Αποθήκευση',
    backToDashboard: 'Πίσω στον πίνακα ελέγχου',
    allFieldsRequired: 'Όλα τα πεδία είναι υποχρεωτικά',

    // Show Appointments
    yourAppointments: 'Τα Ραντεβού σας',
    noAppointmentsYet: 'Δεν υπάρχουν ραντεβού',
    noAppointmentsDesc: 'Μεταβείτε στον πίνακα ελέγχου για να κλείσετε το πρώτο σας.',
    past: 'Παλαιότερα',
    time: 'Ώρα',
    notes: 'Σημειώσεις',
    edit: 'Επεξεργασία',
    delete: 'Διαγραφή',
    confirmDelete: 'Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το ραντεβού;\n\nΑυτή η ενέργεια δεν μπορεί να αναιρεθεί.',
    confirmAccept: 'Αποδοχή αυτού του ραντεβού;',
    confirmDecline: 'Είστε σίγουροι ότι θέλετε να απορρίψετε αυτό το ραντεβού;\n\nΟ πελάτης θα ειδοποιηθεί.',

    // Doctor view
    doctorAppointmentsTitle: 'Ραντεβού Πελατών',
    noAppointmentsScheduled: 'Δεν υπάρχουν ραντεβού',
    noAppointmentsScheduledDesc: 'Οι πελάτες θα κλείσουν ραντεβού μαζί σας σύντομα.',
    clientName: 'Πελάτης',
    cancelAppointment: 'Ακύρωση Ραντεβού',
    acceptAppointment: 'Αποδοχή',
    declineAppointment: 'Απόρριψη',

    // Status
    status: 'Κατάσταση',
    statusPending: 'Σε αναμονή',
    statusConfirmed: 'Επιβεβαιωμένο',
    statusDeclined: 'Απορρίφθηκε',

    // Availability
    availability: 'Διαθεσιμότητα',
    availabilityTitle: 'Εβδομαδιαία Διαθεσιμότητα',
    availabilitySaved: 'Η διαθεσιμότητα αποθηκεύτηκε επιτυχώς',
    addTimeWindow: 'Προσθήκη ωρών',
    remove: 'Αφαίρεση',
    noSlotsAvailable: 'Δεν υπάρχουν διαθέσιμες ώρες για αυτή την ημερομηνία',
    selectDoctorFirst: 'Επιλέξτε πρώτα γιατρό',
    selectDateFirst: 'Επιλέξτε ημερομηνία',
    monday: 'Δευτέρα',
    tuesday: 'Τρίτη',
    wednesday: 'Τετάρτη',
    thursday: 'Πέμπτη',
    friday: 'Παρασκευή',
    saturday: 'Σάββατο',
    sunday: 'Κυριακή',

    // Account
    accountTitle: 'Λογαριασμός',
    back: 'Πίσω',
    failedToLoad: 'Αποτυχία φόρτωσης στοιχείων λογαριασμού',
    editProfile: 'Επεξεργασία Προφίλ',
    currentPassword: 'Τρέχων Κωδικός',
    newPassword: 'Νέος Κωδικός',
    profileUpdated: 'Το προφίλ ενημερώθηκε επιτυχώς',

    // Confirm / Toast
    cancelBtn: 'Ακύρωση',
    confirmDeleteBtn: 'Διαγραφή',
  },
};

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => {
    return localStorage.getItem('lang') || 'el';
  });

  const toggleLang = () => {
    const next = lang === 'en' ? 'el' : 'en';
    setLang(next);
    localStorage.setItem('lang', next);
  };

  const t = translations[lang];

  return (
    <LanguageContext.Provider value={{ lang, toggleLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
