from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.domain.i18n import is_rtl, normalize_locale
from app.domain.users import User
from app.infrastructure.email.smtp import SmtpEmailSender

BRAND = {
    "it": "Comunità Islamica Firenze e Toscana",
    "ar": "الجالية الإسلامية في فلورنسا وتوسكانا",
    "en": "Islamic Community of Florence and Tuscany",
}

MESSAGES: dict[str, dict[str, dict[str, str]]] = {
    "verify_email": {
        "it": {
            "subject": "Conferma il tuo indirizzo email",
            "greeting": "Ciao",
            "body": "Grazie per esserti registrato sul sito della comunità. "
            "Conferma il tuo indirizzo email per completare la registrazione.",
            "button": "Conferma email",
            "note": "Il link scade tra {hours} ore. Se non hai creato tu questo account, "
            "ignora questa email.",
        },
        "ar": {
            "subject": "تأكيد بريدك الإلكتروني",
            "greeting": "مرحباً",
            "body": "شكراً لتسجيلك في موقع الجالية. يرجى تأكيد بريدك الإلكتروني لإكمال التسجيل.",
            "button": "تأكيد البريد الإلكتروني",
            "note": "تنتهي صلاحية هذا الرابط خلال {hours} ساعة. "
            "إذا لم تقم بإنشاء هذا الحساب، يمكنك تجاهل هذه الرسالة.",
        },
        "en": {
            "subject": "Confirm your email address",
            "greeting": "Hello",
            "body": "Thanks for signing up to the community website. "
            "Please confirm your email address to finish creating your account.",
            "button": "Confirm email",
            "note": "This link expires in {hours} hours. If you didn't create this account, "
            "you can ignore this email.",
        },
    },
    "reset_password": {
        "it": {
            "subject": "Reimposta la password",
            "greeting": "Ciao",
            "body": "Abbiamo ricevuto una richiesta per reimpostare la password del tuo account.",
            "button": "Scegli una nuova password",
            "note": "Il link scade tra {minutes} minuti. Se non hai fatto tu la richiesta, "
            "ignora questa email: la password resta invariata.",
        },
        "ar": {
            "subject": "إعادة تعيين كلمة المرور",
            "greeting": "مرحباً",
            "body": "تلقّينا طلباً لإعادة تعيين كلمة مرور حسابك.",
            "button": "اختر كلمة مرور جديدة",
            "note": "تنتهي صلاحية هذا الرابط خلال {minutes} دقيقة. "
            "إذا لم تطلب ذلك، تجاهل هذه الرسالة وستبقى كلمة مرورك كما هي.",
        },
        "en": {
            "subject": "Reset your password",
            "greeting": "Hello",
            "body": "We received a request to reset the password for your account.",
            "button": "Choose a new password",
            "note": "This link expires in {minutes} minutes. If you didn't ask for this, "
            "ignore this email and your password stays the same.",
        },
    },
}


class EmailAuthNotifier:
    """AuthNotifier that sends branded HTML emails in the user's preferred language."""

    def __init__(
        self,
        *,
        sender: SmtpEmailSender,
        web_url: str,
        verify_ttl_hours: int,
        reset_ttl_minutes: int,
    ) -> None:
        self._sender = sender
        self._web_url = web_url.rstrip("/")
        self._ttl = {"hours": verify_ttl_hours, "minutes": reset_ttl_minutes}
        self._templates = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            autoescape=select_autoescape(["html"]),
        )

    def send_verification(self, user: User, token: str) -> None:
        self._send(user, kind="verify_email", page="verify-email", token=token)

    def send_password_reset(self, user: User, token: str) -> None:
        self._send(user, kind="reset_password", page="reset-password", token=token)

    def _send(self, user: User, *, kind: str, page: str, token: str) -> None:
        lang = normalize_locale(user.preferred_locale)
        rtl = is_rtl(lang)
        text = {key: value.format(**self._ttl) for key, value in MESSAGES[kind][lang].items()}
        link = f"{self._web_url}/{lang}/{page}?token={token}"
        comma = "،" if rtl else ","

        html = self._templates.get_template("layout.html").render(
            lang=lang,
            dir="rtl" if rtl else "ltr",
            align="right" if rtl else "left",
            brand=BRAND[lang],
            name=user.full_name,
            comma=comma,
            link=link,
            **text,
        )
        plain = (
            f"{text['greeting']} {user.full_name}{comma}\n\n"
            f"{text['body']}\n\n{link}\n\n{text['note']}\n"
        )
        self._sender.send(to=user.email, subject=text["subject"], html=html, text=plain)