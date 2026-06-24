import { X, Send, CalendarPlus, Search, Clock, UserCheck, Settings2, ChevronDown, ChevronUp, Zap } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChatbotStore } from '../store/useChatbotStore';
import useAuthStore from '../store/useAuthStore';
import api from '../services/api';

const QUICK_ACTIONS = [
  {
    id: 'book',
    icon: CalendarPlus,
    gradient: 'linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)',
  },
  {
    id: 'track',
    icon: Search,
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #10b981 100%)',
  },
  {
    id: 'slots',
    icon: Clock,
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #f43f5e 100%)',
  },
  {
    id: 'doctors',
    icon: UserCheck,
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
  },
  {
    id: 'manage',
    icon: Settings2,
    gradient: 'linear-gradient(135deg, #f43f5e 0%, #f59e0b 100%)',
  },
];

const TRANSLATIONS = {
  en: {
    title: "MedPredict Assistant",
    subtitle: "Always here to help",
    book: 'Book Appointment',
    track: 'Track Appointment',
    slots: 'Available Times',
    doctors: 'Available Doctors',
    manage: 'Manage Appointment',
    quickActions: 'Quick Actions',
    inputPlaceholder: "Type your message...",
    
    book_desc: 'Schedule a new appointment',
    track_desc: 'View your upcoming appointments',
    slots_desc: 'Check available booking slots',
    doctors_desc: 'See our medical team',
    manage_desc: 'Cancel or reschedule',

    book_response: "📅 I'm redirecting you to the booking page where you can:\n\n" +
      "• Choose your preferred doctor\n" +
      "• Select a convenient date & time\n" +
      "• Provide your visit reason\n\n" +
      "Opening booking page now...",
      
    track_no_auth: "📋 To track your appointments, please log in with your patient account.\n\n" +
      "If you don't have an account, book your first appointment and one will be created for you automatically!",
    track_empty: "📭 You don't have any appointments yet.\n\n" +
      "Would you like to book one? Use the 'Book Appointment' quick action!",
    track_title: "📋 **Your Appointments**",
    track_upcoming: "🟢 **Upcoming**",
    track_past: "📁 **Past/Cancelled**",
    track_error: "⚠️ Unable to fetch your appointments right now. Please try again later.",
    
    slots_no_doctors: "⚠️ No doctors are currently available. Please try again later.",
    slots_title: "🕐 **Available Slots for {date}:**\n\n",
    slots_booked: "❌ Fully booked",
    slots_error: "⚠️ Could not check availability",
    slots_no_slots: "\n💡 Try selecting a different date on the booking page for more options!",
    slots_footer: "\n📅 Use 'Book Appointment' to reserve a slot!",
    slots_fetch_error: "⚠️ Unable to check available slots right now. Please try again later.",
    
    doctors_no_doctors: "⚠️ No doctors are currently registered. Please try again later.",
    doctors_title: "👨‍⚕️ **Our Medical Team**",
    doctors_footer: "📅 Use 'Book Appointment' to schedule with any of our doctors!",
    doctors_fetch_error: "⚠️ Unable to fetch doctors list right now. Please try again later.",
    
    manage_no_auth: "🔐 To manage your appointments, please log in with your patient account first.\n\n" +
      "You can then cancel or reschedule from your Patient Portal.",
    manage_empty: "📭 You have no active appointments to manage.\n\n" +
      "Would you like to book a new one? Use 'Book Appointment'!",
    manage_title: "⚙️ **Manage Your Appointments:**\n\n",
    manage_active: "You have active appointments:\n\n",
    manage_footer: "To cancel or reschedule, please:\n" +
      "• 📞 Contact the secretary at the clinic\n" +
      "• 🖥️ Visit your Patient Portal for details\n" +
      "• 💬 Tell me which appointment you'd like to manage",
    manage_error: "⚠️ Unable to fetch your appointments. Please try again or visit the Patient Portal.",
    
    default_error: "I'm not sure how to handle that action. Please try again.",
    general_error: "⚠️ Something went wrong. Please try again.",
    api_error: "Désolé, une erreur est survenue lors de la communication avec l'assistant.",
    doctor_label: "Doctor",
    status_label: "Status",
    minutes: "minutes",
    at_time: "at",
    total: "total",
    and_more: "and {count} more",
  },
  fr: {
    title: "Assistant MedPredict",
    subtitle: "Toujours là pour vous aider",
    book: 'Prendre rendez-vous',
    track: 'Suivre mes rendez-vous',
    slots: 'Créneaux disponibles',
    doctors: 'Médecins disponibles',
    manage: 'Gérer mon rendez-vous',
    quickActions: 'Actions Rapides',
    inputPlaceholder: "Écrivez votre message...",
    
    book_desc: 'Planifier un nouveau rendez-vous',
    track_desc: 'Voir vos rendez-vous à venir',
    slots_desc: 'Vérifier les créneaux disponibles',
    doctors_desc: 'Voir notre équipe médicale',
    manage_desc: 'Annuler ou reporter',

    book_response: "📅 Je vous redirige vers la page de réservation où vous pourrez :\n\n" +
      "• Choisir votre médecin préféré\n" +
      "• Sélectionner une date et heure convenable\n" +
      "• Indiquer le motif de votre visite\n\n" +
      "Redirection en cours...",
      
    track_no_auth: "📋 Pour suivre vos rendez-vous, veuillez vous connecter à votre espace patient.\n\n" +
      "Si vous n'avez pas de compte, réservez un premier rendez-vous et un compte sera créé automatiquement !",
    track_empty: "📭 Vous n'avez pas encore de rendez-vous enregistré.\n\n" +
      "Souhaitez-vous en réserver un ? Utilisez l'action 'Prendre rendez-vous' !",
    track_title: "📋 **Vos Rendez-vous**",
    track_upcoming: "🟢 **À venir**",
    track_past: "📁 **Passés/Annulés**",
    track_error: "⚠️ Impossible de récupérer vos rendez-vous pour le moment. Veuillez réessayer plus tard.",
    
    slots_no_doctors: "⚠️ Aucun médecin n'est disponible actuellement. Veuillez réessayer plus tard.",
    slots_title: "🕐 **Créneaux disponibles pour le {date} :**\n\n",
    slots_booked: "❌ Complet",
    slots_error: "⚠️ Impossible de vérifier la disponibilité",
    slots_no_slots: "\n💡 Essayez de choisir une autre date sur la page de réservation pour plus d'options !",
    slots_footer: "\n📅 Utilisez 'Prendre rendez-vous' pour réserver un créneau !",
    slots_fetch_error: "⚠️ Impossible de vérifier les créneaux disponibles pour le moment.",
    
    doctors_no_doctors: "⚠️ Aucun médecin n'est enregistré pour le moment. Veuillez réessayer plus tard.",
    doctors_title: "👨‍⚕️ **Notre Équipe Médicale**",
    doctors_footer: "📅 Utilisez 'Prendre rendez-vous' pour planifier une consultation !",
    doctors_fetch_error: "⚠️ Impossible de récupérer la liste des médecins pour le moment.",
    
    manage_no_auth: "🔐 Pour gérer vos rendez-vous, veuillez d'abord vous connecter à votre espace patient.\n\n" +
      "Vous pourrez ensuite annuler ou reporter depuis votre Espace Patient.",
    manage_empty: "📭 Vous n'avez aucun rendez-vous actif à gérer.\n\n" +
      "Souhaitez-vous en réserver un nouveau ? Utilisez 'Prendre rendez-vous' !",
    manage_title: "⚙️ **Gérer vos Rendez-vous :**\n\n",
    manage_active: "Vous avez des rendez-vous actifs :\n\n",
    manage_footer: "Pour annuler ou reporter, veuillez :\n" +
      "• 📞 Contacter le secrétariat de la clinique\n" +
      "• 🖥️ Visiter votre Espace Patient pour plus de détails\n" +
      "• 💬 Dites-moi quel rendez-vous vous souhaitez gérer",
    manage_error: "⚠️ Impossible de récupérer vos rendez-vous. Veuillez réessayer ou visiter l'Espace Patient.",
    
    default_error: "Je ne sais pas comment gérer cette action. Veuillez réessayer.",
    general_error: "⚠️ Une erreur est survenue. Veuillez réessayer.",
    api_error: "Désolé, une erreur est survenue lors de la communication avec l'assistant.",
    doctor_label: "Médecin",
    status_label: "Statut",
    minutes: "minutes",
    at_time: "à",
    total: "au total",
    and_more: "et {count} autres",
  },
  ar: {
    title: "مساعد MedPredict",
    subtitle: "هنا لمساعدتك دائمًا",
    book: 'حجز موعد',
    track: 'تتبع مواعيدي',
    slots: 'الأوقات المتاحة',
    doctors: 'الأطباء المتاحون',
    manage: 'إدارة موعدي',
    quickActions: 'إجراءات سريعة',
    inputPlaceholder: "اكتب رسالتك هنا...",
    
    book_desc: 'جدولة موعد جديد',
    track_desc: 'عرض مواعيدك القادمة',
    slots_desc: 'التحقق من الفترات المتاحة',
    doctors_desc: 'رؤية طاقمنا الطبي',
    manage_desc: 'إلغاء أو إعادة جدولة',

    book_response: "📅 جاري تحويلك إلى صفحة الحجز حيث يمكنك:\n\n" +
      "• اختيار طبيبك المفضل\n" +
      "• اختيار التاريخ والوقت المناسبين\n" +
      "• تحديد سبب الزيارة\n\n" +
      "جاري فتح صفحة الحجز الآن...",
      
    track_no_auth: "📋 لتتبع مواعيدك، يرجى تسجيل الدخول إلى حساب المريض الخاص بك.\n\n" +
      "إذا لم يكن لديك حساب، فقم بحجز موعدك الأول وسيتم إنشاء حساب لك تلقائيًا!",
    track_empty: "📭 ليس لديك أي مواعيد مسجلة بعد.\n\n" +
      "هل تود حجز موعد؟ استخدم خيار 'حجز موعد' السريع!",
    track_title: "📋 **مواعيدك**",
    track_upcoming: "🟢 **القادمة**",
    track_past: "📁 **السابقة/الملغاة**",
    track_error: "⚠️ تعذر جلب مواعيدك الآن. يرجى المحاولة مرة أخرى لاحقًا.",
    
    slots_no_doctors: "⚠️ لا يوجد أطباء متاحون حاليًا. يرجى المحاولة لاحقًا.",
    slots_title: "🕐 **الأوقات المتاحة ليوم {date}:**\n\n",
    slots_booked: "❌ محجوز بالكامل",
    slots_error: "⚠️ تعذر التحقق من التوفر",
    slots_no_slots: "\n💡 حاول اختيار تاريخ آخر في صفحة الحجز لمزيد من الخيارات!",
    slots_footer: "\n📅 استخدم 'حجز موعد' لحجز وقت!",
    slots_fetch_error: "⚠️ تعذر التحقق من الأوقات المتاحة حاليًا. يرجى المحاولة لاحقًا.",
    
    doctors_no_doctors: "⚠️ لا يوجد أطباء مسجلون حاليًا. يرجى المحاولة لاحقًا.",
    doctors_title: "👨‍⚕️ **طاقمنا الطبي**",
    doctors_footer: "📅 استخدم 'حجز موعد' للجدولة مع أي من أطبائنا!",
    doctors_fetch_error: "⚠️ تعذر جلب قائمة الأطباء حاليًا. يرجى المحاولة لاحقًا.",
    
    manage_no_auth: "🔐 لإدارة مواعيدك، يرجى تسجيل الدخول أولاً.\n\n" +
      "يمكنك بعد ذلك الإلغاء أو إعادة الجدولة من حسابك.",
    manage_empty: "📭 ليس لديك مواعيد نشطة لإدارتها.\n\n" +
      "هل تود حجز موعد جديد؟ استخدم 'حجز موعد'!",
    manage_title: "⚙️ **إدارة مواعيدك:**\n\n",
    manage_active: "لديك مواعيد نشطة:\n\n",
    manage_footer: "للإلغاء أو إعادة الجدولة، يرجى:\n" +
      "• 📞 الاتصال بسكرتارية العيادة\n" +
      "• 🖥️ زيارة حساب المريض الخاص بك لمزيد من التفاصيل\n" +
      "• 💬 أخبرني بأي موعد ترغب في إدارته",
    manage_error: "⚠️ تعذر جلب مواعيدك. يرجى المحاولة مرة أخرى أو زيارة حساب المريض.",
    
    default_error: "أنا لست متأكدًا من كيفية التعامل مع هذا الإجراء. يرجى المحاولة مرة أخرى.",
    general_error: "⚠️ حدث خطأ ما. يرجى المحاولة مرة أخرى.",
    api_error: "عذرًا، حدث خطأ أثناء الاتصال بالمساعد الطبي.",
    doctor_label: "الطبيب",
    status_label: "الحالة",
    minutes: "دقائق",
    at_time: "على الساعة",
    total: "الإجمالي",
    and_more: "و {count} مواعيد أخرى",
  },
  darija: {
    title: "مساعد MedPredict",
    subtitle: "ديما واجد يعاونك",
    book: 'نأخذ موعد',
    track: 'نتبع المواعيد ديالي',
    slots: 'الأوقات الخاوية',
    doctors: 'الطباء اللي كاينين',
    manage: 'نبدل ولا نلغي الموعد',
    quickActions: 'إجراءات دغيا دغيا',
    inputPlaceholder: "اكتب الميساج ديالك هنا...",
    
    book_desc: 'تقيد موعد جديد',
    track_desc: 'تشوف المواعيد اللي عندك',
    slots_desc: 'تشوف الأوقات اللي خاوية',
    doctors_desc: 'تشوف الفرقة الطبية ديالنا',
    manage_desc: 'تبدل ولا تلغي موعد',

    book_response: "📅 هاني غانديك لصفحة الحجز فين تقدر :\n\n" +
      "• تختار الطبيب اللي بغيتي\n" +
      "• تعزل النهار والوقت اللي مسلكينك\n" +
      "• تكتب علاش باغي تدوز\n\n" +
      "بلاتي شوية، الصفحة غاتحل...",
      
    track_no_auth: "📋 باش تتبع المواعيد ديالك، خاصك تكون داخل بالحساب ديالك.\n\n" +
      "إيلا ماعندكش حساب، قيد الموعد اللول ديالك وغايتكريا ليك حساب أوتوماتيكيا!",
    track_empty: "📭 ما عندك حتى شي موعد مقيد دابا.\n\n" +
      "واش بغيتي تقيد شي موعد؟ تورك على 'نأخذ موعد'!",
    track_title: "📋 **المواعيد ديالك**",
    track_upcoming: "🟢 **اللي جايين**",
    track_past: "📁 **اللي فاتو ولا تلغاو**",
    track_error: "⚠️ ما قدرناش نجيبو المواعيد ديالك دابا. عاود جرب من بعد عفاك.",
    
    slots_no_doctors: "⚠️ ما كاين حتى طبيب دابا. جرب من بعد عفاك.",
    slots_title: "🕐 **الأوقات اللي خاوية نهار {date}:**\n\n",
    slots_booked: "❌ عامر بالكامل",
    slots_error: "⚠️ ما قدرناش نشوفو واش خاوي",
    slots_no_slots: "\n💡 جرب تعزل نهار آخر فصفحة الحجز باش تلقى أوقات أخرى!",
    slots_footer: "\n📅 ورك على 'نأخذ موعد' باش تحجز الوقت ديالك!",
    slots_fetch_error: "⚠️ ما قدرناش نشوفو المواعيد الخاوية دابا. عاود جرب من بعد عفاك.",
    
    doctors_no_doctors: "⚠️ ما كاين حتى طبيب مقيد دابا. عاود جرب من بعد.",
    doctors_title: "👨‍⚕️ **الفرقة الطبية ديالنا**",
    doctors_footer: "📅 ورك على 'نأخذ موعد' باش تدوز عند شي طبيب ديالنا!",
    doctors_fetch_error: "⚠️ ما قدرناش نجيبو ليستة ديال الطباء دابا. عاود جرب من بعد عفاك.",
    
    manage_no_auth: "🔐 باش تبدل المواعيد ديالك، خاصك تكون داخل لحساب المريض ديالك أولا.\n\n" +
      "من بعد تقدر تلغي ولا تبدل الوقت نيشان من الحساب ديالك.",
    manage_empty: "📭 ما عندك حتى موعد دابا باش تبدلو.\n\n" +
      "بغيتي تقيد موعد جديد؟ ورك على 'نأخذ موعد'!",
    manage_title: "⚙️ **تبدال المواعيد ديالك:**\n\n",
    manage_active: "عندك هاد المواعيد مقيدة دابا:\n\n",
    manage_footer: "باش تلغي ولا تبدل الوقت، عفاك:\n" +
      "• 📞 عيط للسكرتارية فالكلينيك\n" +
      "• 🖥️ دخل لحساب المريض ديالك باش تشوف كاع التفاصيل\n" +
      "• 💬 قولي أين موعد بغيتي تبدل ولا تلغي",
    manage_error: "⚠️ ما قدرناش نجيبو المواعيد ديالك. عاود جرب من بعد عفاك.",
    
    default_error: "ما عرفتش كيفاش ندير لهاد القضية. عاود جرب عفاك.",
    general_error: "⚠️ وقع شي غلط. عاود جرب عفاك.",
    api_error: "سمح لينا، كاين شي مشكل فالاتصال مع المساعد الطبي.",
    doctor_label: "الطبيب",
    status_label: "الحالة",
    minutes: "دقائق",
    at_time: "مع",
    total: "المجموع",
    and_more: "و {count} خرين",
  }
};

export default function ChatbotWindow() {
  const { isOpen, messages, addMessage } = useChatbotStore();
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [processingAction, setProcessingAction] = useState(null);
  const [lang, setLang] = useState('fr');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const textToSend = inputValue.trim();
    if (textToSend) {
      addMessage(textToSend, 'user');
      setInputValue('');
      setIsTyping(true);

      try {
        const historyData = messages.map(m => ({ type: m.type, text: m.text }));
        const res = await api.post('/auth/chatbot/', {
          message: textToSend,
          history: historyData,
          language: lang
        });
        addMessage(res.data.reply, 'bot');
      } catch (err) {
        console.error(err);
        addMessage(TRANSLATIONS[lang].api_error, 'bot');
      } finally {
        setIsTyping(false);
      }
    }
  };

  const formatDate = (dateStr, currentLang = 'en') => {
    const d = new Date(dateStr + 'T00:00:00');
    const locale = currentLang === 'ar' || currentLang === 'darija' ? 'ar-MA' : currentLang === 'fr' ? 'fr-FR' : 'en-US';
    return d.toLocaleDateString(locale, { weekday: 'short', day: 'numeric', month: 'short' });
  };

  const getStatusEmoji = (status) => {
    switch (status) {
      case 'PLANNED': return '🕐';
      case 'CONFIRMED': return '✅';
      case 'IN_PROGRESS': return '🔄';
      case 'COMPLETED': return '✔️';
      case 'CANCELLED': return '❌';
      default: return '📋';
    }
  };

  const getStatusLabel = (status, currentLang = 'en') => {
    const labels = {
      en: { PLANNED: 'Planned', CONFIRMED: 'Confirmed', IN_PROGRESS: 'In Progress', COMPLETED: 'Completed', CANCELLED: 'Cancelled' },
      fr: { PLANNED: 'Planifié', CONFIRMED: 'Confirmé', IN_PROGRESS: 'En cours', COMPLETED: 'Terminé', CANCELLED: 'Annulé' },
      ar: { PLANNED: 'مخطط', CONFIRMED: 'مؤكد', IN_PROGRESS: 'قيد التنفيذ', COMPLETED: 'مكتمل', CANCELLED: 'ملغى' },
      darija: { PLANNED: 'مخطط', CONFIRMED: 'مؤكد', IN_PROGRESS: 'باقي ماداز', COMPLETED: 'داز', CANCELLED: 'ملغي' }
    };
    return labels[currentLang]?.[status] || status;
  };

  const handleQuickAction = async (actionId) => {
    if (processingAction) return;
    setProcessingAction(actionId);
    setShowQuickActions(false);

    const action = QUICK_ACTIONS.find(a => a.id === actionId);
    addMessage(`⚡ ${TRANSLATIONS[lang][actionId]}`, 'user');
    setIsTyping(true);

    try {
      switch (actionId) {
        case 'book': {
          addMessage(TRANSLATIONS[lang].book_response, 'bot');
          setTimeout(() => {
            navigate('/book');
          }, 1500);
          break;
        }

        case 'track': {
          if (!user || user.role !== 'PATIENT') {
            addMessage(TRANSLATIONS[lang].track_no_auth, 'bot');
            break;
          }

          try {
            const res = await api.get('/appointments/my/');
            const appointments = res.data;

            if (!appointments || appointments.length === 0) {
              addMessage(TRANSLATIONS[lang].track_empty, 'bot');
            } else {
              const upcoming = appointments.filter(
                a => a.status !== 'CANCELLED' && a.status !== 'COMPLETED'
              );
              const past = appointments.filter(
                a => a.status === 'CANCELLED' || a.status === 'COMPLETED'
              );

              let reply = `📋 **${TRANSLATIONS[lang].track_title}** (${appointments.length} ${TRANSLATIONS[lang].total})\n\n`;

              if (upcoming.length > 0) {
                reply += `${TRANSLATIONS[lang].track_upcoming} (${upcoming.length}):\n`;
                upcoming.forEach((a, i) => {
                  const doctor = a.doctor_details
                    ? `Dr. ${a.doctor_details.first_name} ${a.doctor_details.last_name}`
                    : `${TRANSLATIONS[lang].doctor_label} #${a.doctor}`;
                  reply += `${i + 1}. ${getStatusEmoji(a.status)} ${formatDate(a.date, lang)} ${TRANSLATIONS[lang].at_time} ${a.time?.substring(0, 5)} — ${doctor} (${getStatusLabel(a.status, lang)})\n`;
                });
              }

              if (past.length > 0) {
                reply += `\n${TRANSLATIONS[lang].track_past} (${past.length}):\n`;
                past.slice(0, 3).forEach((a, i) => {
                  reply += `${i + 1}. ${getStatusEmoji(a.status)} ${formatDate(a.date, lang)} — ${getStatusLabel(a.status, lang)}\n`;
                });
                if (past.length > 3) {
                  reply += `   ... ${TRANSLATIONS[lang].and_more.replace('{count}', past.length - 3)}\n`;
                }
              }

              addMessage(reply, 'bot');
            }
          } catch (err) {
            console.error(err);
            addMessage(TRANSLATIONS[lang].track_error, 'bot');
          }
          break;
        }

        case 'slots': {
          try {
            const doctorsRes = await api.get('/appointments/public/doctors/');
            const doctors = doctorsRes.data;

            if (!doctors || doctors.length === 0) {
              addMessage(TRANSLATIONS[lang].slots_no_doctors, 'bot');
              break;
            }

            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            const dateStr = tomorrow.toISOString().split('T')[0];

            let reply = TRANSLATIONS[lang].slots_title.replace('{date}', formatDate(dateStr, lang));
            let hasAnySlots = false;

            for (const doc of doctors.slice(0, 3)) {
              try {
                const slotsRes = await api.get(`/appointments/public/available-slots/?doctor_id=${doc.id}&date=${dateStr}`);
                const slots = slotsRes.data;

                reply += `👨‍⚕️ **Dr. ${doc.first_name} ${doc.last_name}**\n`;
                if (slots && slots.length > 0) {
                  reply += `   ${slots.join(' • ')}\n\n`;
                  hasAnySlots = true;
                } else {
                  reply += `   ${TRANSLATIONS[lang].slots_booked}\n\n`;
                }
              } catch {
                reply += `   ${TRANSLATIONS[lang].slots_error}\n\n`;
              }
            }

            if (!hasAnySlots) {
              reply += TRANSLATIONS[lang].slots_no_slots;
            }

            reply += TRANSLATIONS[lang].slots_footer;
            addMessage(reply, 'bot');
          } catch (err) {
            console.error(err);
            addMessage(TRANSLATIONS[lang].slots_fetch_error, 'bot');
          }
          break;
        }

        case 'doctors': {
          try {
            const res = await api.get('/appointments/public/doctors/');
            const doctors = res.data;

            if (!doctors || doctors.length === 0) {
              addMessage(TRANSLATIONS[lang].doctors_no_doctors, 'bot');
              break;
            }

            let reply = `👨‍⚕️ **${TRANSLATIONS[lang].doctors_title}** (${doctors.length} ${TRANSLATIONS[lang].doctor_label.toLowerCase()}${doctors.length > 1 ? 's' : ''}):\n\n`;
            doctors.forEach((doc, i) => {
              reply += `${i + 1}. **Dr. ${doc.first_name} ${doc.last_name}**\n`;
              reply += `   🏥 ${doc.specialty || 'Médecine Générale'}\n\n`;
            });

            reply += TRANSLATIONS[lang].doctors_footer;
            addMessage(reply, 'bot');
          } catch (err) {
            console.error(err);
            addMessage(TRANSLATIONS[lang].doctors_fetch_error, 'bot');
          }
          break;
        }

        case 'manage': {
          if (!user || user.role !== 'PATIENT') {
            addMessage(TRANSLATIONS[lang].manage_no_auth, 'bot');
            break;
          }

          try {
            const res = await api.get('/appointments/my/');
            const appointments = res.data;
            const active = appointments.filter(
              a => a.status !== 'CANCELLED' && a.status !== 'COMPLETED'
            );

            if (active.length === 0) {
              addMessage(TRANSLATIONS[lang].manage_empty, 'bot');
            } else {
              let reply = TRANSLATIONS[lang].manage_title;
              reply += `${TRANSLATIONS[lang].manage_active}\n\n`;

              active.forEach((a, i) => {
                const doctor = a.doctor_details
                  ? `Dr. ${a.doctor_details.first_name} ${a.doctor_details.last_name}`
                  : `${TRANSLATIONS[lang].doctor_label} #${a.doctor}`;
                reply += `${i + 1}. ${getStatusEmoji(a.status)} **${formatDate(a.date, lang)}** ${TRANSLATIONS[lang].at_time} ${a.time?.substring(0, 5)}\n`;
                reply += `   ${doctor} — ${a.reason}\n`;
                reply += `   ${TRANSLATIONS[lang].status_label}: ${getStatusLabel(a.status, lang)}\n\n`;
              });

              reply += TRANSLATIONS[lang].manage_footer;
              addMessage(reply, 'bot');
            }
          } catch (err) {
            console.error(err);
            addMessage(TRANSLATIONS[lang].manage_error, 'bot');
          }
          break;
        }

        default:
          addMessage(TRANSLATIONS[lang].default_error, 'bot');
      }
    } catch (err) {
      console.error(err);
      addMessage(TRANSLATIONS[lang].general_error, 'bot');
    } finally {
      setIsTyping(false);
      setProcessingAction(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed bottom-24 right-8 w-96 rounded-2xl shadow-2xl flex flex-col z-50 animate-slideUp"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: `1px solid var(--glass-border)`,
        height: '540px',
      }}
    >
      {/* Header */}
      <div 
        className="p-4 rounded-t-2xl flex justify-between items-center text-white"
        style={{
          background: `linear-gradient(to right, var(--primary), var(--secondary))`,
        }}
      >
        <div>
          <h3 className="font-semibold text-base m-0 leading-tight">{TRANSLATIONS[lang].title}</h3>
          <p className="text-[11px] opacity-90 m-0 mt-0.5">{TRANSLATIONS[lang].subtitle}</p>
        </div>
        
        {/* Language Switcher Dropdown */}
        <div className="flex items-center gap-1.5">
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value)}
            className="text-xs bg-white/20 border border-white/20 text-white rounded px-1.5 py-0.5 outline-none cursor-pointer font-bold transition-all hover:bg-white/30"
            style={{
              backdropFilter: 'blur(4px)',
            }}
          >
            <option value="fr" style={{ color: 'black' }}>FR</option>
            <option value="en" style={{ color: 'black' }}>EN</option>
            <option value="ar" style={{ color: 'black' }}>AR</option>
            <option value="darija" style={{ color: 'black' }}>Darija</option>
          </select>
        </div>
      </div>

      {/* Messages Container */}
      <div 
        className="flex-1 overflow-y-auto p-4 space-y-3"
        style={{
          backgroundColor: 'var(--bg-main)',
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.type === 'user'
                  ? 'rounded-br-none'
                  : 'rounded-bl-none'
              }`}
              dir={lang === 'ar' || lang === 'darija' ? 'rtl' : 'ltr'}
              style={{
                backgroundColor: msg.type === 'user' ? 'var(--primary)' : 'var(--bg-card)',
                color: msg.type === 'user' ? 'white' : 'var(--text-main)',
                border: msg.type === 'user' ? 'none' : `1px solid var(--glass-border)`,
              }}
            >
              <p className="text-sm" style={{ whiteSpace: 'pre-line' }}>{msg.text}</p>
              <span 
                className="text-xs mt-1 block"
                style={{
                  color: msg.type === 'user' ? 'rgba(255, 255, 255, 0.7)' : 'var(--text-light)',
                  textAlign: lang === 'ar' || lang === 'darija' ? 'left' : 'right'
                }}
              >
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div 
              className="max-w-xs px-4 py-2 rounded-lg rounded-bl-none"
              style={{
                backgroundColor: 'var(--bg-card)',
                color: 'var(--text-main)',
                border: `1px solid var(--glass-border)`,
              }}
            >
              <div className="flex items-center gap-1.5 py-1">
                <span className="chatbot-typing-dot" style={{ animationDelay: '0ms' }}></span>
                <span className="chatbot-typing-dot" style={{ animationDelay: '150ms' }}></span>
                <span className="chatbot-typing-dot" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions Panel */}
      <div
        style={{
          borderTop: `1px solid var(--glass-border)`,
          backgroundColor: 'var(--bg-card)',
        }}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setShowQuickActions(!showQuickActions)}
          className="chatbot-quick-actions-toggle"
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.4rem',
            padding: '0.5rem',
            border: 'none',
            background: 'transparent',
            color: 'var(--primary)',
            cursor: 'pointer',
            fontSize: '0.75rem',
            fontWeight: 700,
            fontFamily: 'var(--font-base)',
            letterSpacing: '0.03em',
            transition: 'all 0.2s ease',
          }}
        >
          <Zap size={13} />
          {TRANSLATIONS[lang].quickActions}
          {showQuickActions ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
        </button>

        {/* Actions Grid */}
        {showQuickActions && (
          <div className="chatbot-quick-actions-grid" style={{ padding: '0 0.75rem 0.75rem' }}>
            {QUICK_ACTIONS.map((action, index) => {
              const Icon = action.icon;
              const isProcessing = processingAction === action.id;
              return (
                <button
                  key={action.id}
                  onClick={() => handleQuickAction(action.id)}
                  disabled={!!processingAction}
                  className="chatbot-quick-action-btn"
                  style={{
                    '--action-gradient': action.gradient,
                    animationDelay: `${index * 50}ms`,
                    opacity: isProcessing ? 0.7 : 1,
                  }}
                  title={TRANSLATIONS[lang][action.id + '_desc']}
                >
                  <span className="chatbot-quick-action-icon-wrapper" style={{ background: action.gradient }}>
                    <Icon size={11} strokeWidth={2.5} />
                  </span>
                  <span className="chatbot-quick-action-label">
                    {isProcessing ? '...' : TRANSLATIONS[lang][action.id]}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Input Area */}
      <form 
        onSubmit={handleSendMessage} 
        className="p-4 rounded-b-2xl"
        style={{
          borderTop: `1px solid var(--glass-border)`,
          backgroundColor: 'var(--bg-card)',
        }}
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={TRANSLATIONS[lang].inputPlaceholder}
            dir={lang === 'ar' || lang === 'darija' ? 'rtl' : 'ltr'}
            className="flex-1 px-4 py-2 rounded-lg focus:outline-none transition-all text-sm"
            style={{
              backgroundColor: 'var(--bg-main)',
              color: 'var(--text-main)',
              border: `1px solid var(--glass-border)`,
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--primary)';
              e.target.style.boxShadow = `0 0 0 3px var(--primary-light)`;
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--glass-border)';
              e.target.style.boxShadow = 'none';
            }}
          />
          <button
            type="submit"
            className="text-white px-4 py-2 rounded-lg transition-all hover:shadow-lg flex items-center gap-2"
            style={{
              backgroundColor: 'var(--primary)',
            }}
          >
            <Send size={16} />
          </button>
        </div>
      </form>
    </div>
  );
}
