from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from .models import Admin, User, OriginalDocument, VerificationHistory, DigiLocker, Contact, UserDocument
import hashlib

def generate_hash(file):

    sha256 = hashlib.sha256()

    for chunk in file.chunks():
        sha256.update(chunk)

    return sha256.hexdigest()
# ==========================
# Home
# ==========================

def home(request):
    return render(request, 'index.html')


def chart(request):
    return render(request, 'chart.html')


WEBSITE_CONTEXT = """
You are a helpful general-purpose AI assistant built into the True File website.
Answer questions from any subject or domain: technology, education, science,
business, writing, travel, everyday life, and other general topics. Be accurate,
clear, friendly, and honest about uncertainty. For questions about this website,
give extra detailed and practical guidance based on the True File workflow below.

True File is a document verification system.
Website features:
- Users can register, log in, view their profile, upload documents to True Wallet,
    verify a document, and view verification history.
- Administrators can register, log in, upload original reference documents,
    view the blockchain ledger, view verification reports, and delete documents.
- Verification calculates a SHA-256 hash. A matching stored hash means the file
    matches an uploaded original; a missing match is reported as tampered or fake.
- The ledger stores each document hash, the previous block hash, the current block
    hash, document type, upload date, and verification status.
- The assistant can answer general questions across any domain, but it must not
    invent a document's verification result. Users must upload the file through
    the verification page for an actual result.
Explain the True File process when relevant: register or log in, upload a reference
document as an administrator, upload a document on Upload Verification, compare
its SHA-256 hash with the stored original, and review the result in Verification
History or the administrator reports and ledger.
Give useful answers with enough detail to solve the user's question. When relevant,
mention the website page or action to use. Do not say that you can only answer a
fixed list of topics.
"""


@csrf_exempt
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are supported."}, status=405)

    try:
        payload = json.loads(request.body)
        message = str(payload.get("message", "")).strip()
        if not message:
            return JsonResponse({"error": "Please enter a message."}, status=400)

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return JsonResponse({"reply": local_chat_reply(message)})

        request_body = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": WEBSITE_CONTEXT},
                {"role": "user", "content": message},
            ],
        }).encode("utf-8")
        api_request = Request(
            "https://api.openai.com/v1/chat/completions",
            data=request_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urlopen(api_request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))

        reply = result["choices"][0]["message"]["content"]
        return JsonResponse({"reply": reply})
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        return JsonResponse(
            {"error": f"OpenAI request failed ({error.code}): {details}"},
            status=502,
        )
    except (URLError, TimeoutError):
        return JsonResponse(
            {"error": "The AI service could not be reached. Try again."},
            status=502,
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"error": "The AI service returned an invalid response."}, status=502)


def local_chat_reply(message):
    """Provide a useful local response when an external AI key is unavailable."""
    text = message.lower()
    if any(word in text.split() for word in ("hello", "hi", "hey")):
        return "Hello! I am ready to help you verify documents or navigate True File."
    if any(word in text for word in ("about", "website", "docverify", "true file", "truefile")):
        return "True File helps organizations check document authenticity using file hashes and a linked verification ledger. It supports user accounts, administrator tools, True Wallet storage, and verification reports."
    if any(word in text for word in ("verify", "original", "fake", "tampered")):
        return "Open Upload Verification and submit your document. True File calculates its SHA-256 hash and compares it with stored originals."
    if "digilocker" in text or "true wallet" in text or "truewallet" in text:
        return "After signing in, use True Wallet to store a document. Your uploaded documents are listed on the True Wallet page."
    if any(word in text for word in ("blockchain", "ledger", "hash")):
        return "The Blockchain Ledger shows each document hash, previous hash, current block hash, document type, date, and status. SHA-256 creates a unique fingerprint for a file."
    if any(word in text for word in ("admin", "administrator", "report")):
        return "Administrators can use Admin Dashboard, Upload Document, Blockchain Ledger, and Verification Reports to manage reference documents and review activity."
    if any(word in text for word in ("history", "profile", "login", "register")):
        return "Users can register or log in, open My Profile, and review past checks in Verification History."
    if any(word in text for word in ("help", "what can", "features", "how does")):
        return "I can answer general questions on many subjects and explain how True File works. For True File, you can register or log in, store documents in True Wallet, upload a document for verification, and review the SHA-256 result in Verification History. Ask me anything, or tell me which True File page you want to use."
    return "I can help with general questions across many subjects. I can also explain True File: users log in, store documents in True Wallet, upload a document through Upload Verification, and compare its SHA-256 hash with the stored original. Ask your question with as much detail as you like."


# ==========================
# Admin Login
# ==========================

def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin = Admin.objects.get(
                username=username,
                password=password
            )

            request.session["admin_id"] = admin.id
            request.session["admin_name"] = admin.name

            return redirect("admin_dashboard")

        except Admin.DoesNotExist:

            return render(request,
                          "admin_login.html",
                          {"error": "Invalid Username or Password"})

    return render(request, "admin_login.html")


# ==========================
# Admin Register
# ==========================

def admin_register(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        password = request.POST.get("password")

        Admin.objects.create(

            name=name,
            email=email,
            phone=phone,
            username=username,
            password=password

        )

        return redirect("admin_login")

    return render(request, "admin_register.html")


# ==========================
# Admin Dashboard
# ==========================

from .models import User, OriginalDocument, VerificationHistory

def admin_dashboard(request):

    total_users = User.objects.count()

    total_documents = OriginalDocument.objects.count()

    total_verified = OriginalDocument.objects.filter(status="Verified").count()

    total_history = VerificationHistory.objects.count()

    context = {

        "total_users": total_users,

        "total_documents": total_documents,

        "total_verified": total_verified,

        "total_history": total_history,

    }

    return render(request, "admin_dashboard.html", context)


# ==========================
# Upload Original Document
# ==========================

import hashlib

def generate_hash(file):
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()

def upload_document(request):

    if request.method == "POST":

        document_name = request.POST.get("document_name")
        document_type = request.POST.get("document_type")
        uploaded_file = request.FILES["document"]

        # Generate SHA-256 Hash
        file_hash = generate_hash(uploaded_file)

        # Reset file pointer
        uploaded_file.seek(0)

        # Get Previous Block Hash
        last_doc = OriginalDocument.objects.last()

        if last_doc:
            previous_hash = last_doc.block_hash
        else:
            previous_hash = "GENESIS"

        # Generate Current Block Hash
        block_hash = hashlib.sha256(
            (file_hash + previous_hash).encode()
        ).hexdigest()

        # Save Original Document
        OriginalDocument.objects.create(
            document_name=document_name,
            document_type=document_type,
            uploaded_file=uploaded_file,
            sha256_hash=file_hash,
            previous_hash=previous_hash,
            block_hash=block_hash,
            status="Verified"
        )

        # Save Verification History
        VerificationHistory.objects.create(
            user_name=request.session.get("admin_name", "Admin"),
            document_name=document_name,
            document_type=document_type,
            result="Original"
        )
        Verification.objects.create(
    verification_id="VR" + str(Verification.objects.count() + 1),
    document_name=uploaded_file.name,
    generated_hash=file_hash,
    blockchain_hash="Not Found",
    status="Tampered"
)

        return render(
            request,
            "upload_document.html",
            {
                "success": "Document Uploaded Successfully!"
            }
        )

    return render(request, "upload_document.html")
# Delete Document
# ==========================

def delete_document(request, id):

    try:

        document = OriginalDocument.objects.get(id=id)

        document.delete()

    except OriginalDocument.DoesNotExist:
        pass

    return redirect("verification_reports")

# ==========================
# Blockchain Ledger
# ==========================

def blockchain_ledger(request):

    documents = OriginalDocument.objects.all().order_by("-id")

    return render(
        request,
        "blockchain_ledger.html",
        {
            "documents": documents
        }
    )


# ==========================
# Verification Reports
# ==========================

# ==========================
# Verification Reports
# ==========================

def verification_reports(request):

    documents = OriginalDocument.objects.all().order_by("-id")

    return render(
        request,
        "verification_reports.html",
        {
            "documents": documents
        }
    )

# ==========================
# User Login
# ==========================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:

            user = User.objects.get(
                username=username,
                password=password
            )

            request.session["user_id"] = user.id
            request.session["user_name"] = user.name

            return redirect("user_dashboard")

        except User.DoesNotExist:

            return render(
                request,
                "user_login.html",
                {
                    "error": "Invalid Username or Password"
                }
            )

    return render(request, "user_login.html")


# ==========================
# User Register
# ==========================

def user_register(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            return render(
                request,
                "user_register.html",
                {
                    "error": "Username already exists."
                }
            )

        User.objects.create(

            name=name,
            email=email,
            phone=phone,
            username=username,
            password=password

        )

        return redirect("user_login")

    return render(request, "user_register.html")


# ==========================
# User Dashboard
# ==========================

def user_dashboard(request):
    return render(request, "user_dashboard.html")


def get_logged_in_user_name(request):
    """Resolve the display name from the logged-in user record."""
    user_id = request.session.get("user_id")
    if user_id:
        user = User.objects.filter(id=user_id).only("name").first()
        if user and user.name:
            return user.name
    return request.session.get("user_name", "User")


# ==========================
# My Profile
# ==========================

def my_profile(request):

    if "user_id" not in request.session:
        return redirect("user_login")

    user = User.objects.get(id=request.session["user_id"])

    return render(
        request,
        "my_profile.html",
        {
            "user": user
        }
    )

    # ==========================
# Upload to DigiLocker
# ==========================

# ==========================
# Upload Document to DigiLocker
# ==========================


import hashlib

def upload_digilocker(request):

    if "user_id" not in request.session:
        return redirect("user_login")

    if request.method == "POST":

        user = User.objects.get(id=request.session["user_id"])

        document_name = request.POST.get("document_name")
        document_type = request.POST.get("document_type")
        document_file = request.FILES.get("document")

        # Generate SHA-256 Hash
        file_hash = generate_hash(document_file)

        # Reset file pointer
        document_file.seek(0)

        # Get Previous Block Hash
        last_doc = OriginalDocument.objects.last()

        if last_doc:
            previous_hash = last_doc.block_hash
        else:
            previous_hash = "GENESIS"

        # Generate Private Blockchain Hash
        block_hash = hashlib.sha256(
            (file_hash + previous_hash).encode()
        ).hexdigest()

        # Save in DigiLocker
        DigiLocker.objects.create(
            user=user,
            document_name=document_name,
            document_type=document_type,
            document_file=document_file
        )

        # Save in Blockchain
        OriginalDocument.objects.create(
            document_name=document_name,
            document_type=document_type,
            uploaded_file=document_file,
            sha256_hash=file_hash,
            previous_hash=previous_hash,
            block_hash=block_hash,
            status="Verified"
        )

        return render(
            request,
            "upload_digilocker.html",
            {
                "success": "Document uploaded successfully!",
                "hash": file_hash,
                "block_hash": block_hash
            }
        )

    return render(request, "upload_digilocker.html")
# ==========================
# Upload Verification
# ==========================

# ==========================
# Upload Verification
# ==========================

def upload_verification(request):

    if request.method == "POST":

        uploaded_file = request.FILES["document"]

        # Generate SHA-256 hash
        file_hash = generate_hash(uploaded_file)

        # Reset file pointer
        uploaded_file.seek(0)

        try:
            document = OriginalDocument.objects.get(sha256_hash=file_hash)

            # Save Verification History
            VerificationHistory.objects.create(
                user_name=get_logged_in_user_name(request),
                document_name=document.document_name,
                document_type=document.document_type,
                result="Original"
            )

            return render(
                request,
                "verification_result.html",
                {
                    "status": "Original Document",
                    "color": "green",
                    "document": document
                }
            )

        except OriginalDocument.DoesNotExist:

            # Save Verification History
            VerificationHistory.objects.create(
                user_name=get_logged_in_user_name(request),
                document_name=uploaded_file.name,
                document_type="Unknown",
                result="Tampered"
            )

            return render(
                request,
                "verification_result.html",
                {
                    "status": "Tampered / Fake Document",
                    "color": "red"
                }
            )

    return render(request, "upload_verification.html")
# ==========================
# Verification Result
# ==========================



# ==========================
# DigiLocker
# ==========================

def digilocker(request):

    if "user_id" not in request.session:
        return redirect("user_login")

    user = User.objects.get(id=request.session["user_id"])

    documents = DigiLocker.objects.filter(user=user)

    return render(
        request,
        "digilocker.html",
        {
            "documents": documents
        }
    )
# ==========================
# Verification History
# ==========================

from .models import Verification

def verification_history(request):

    history = VerificationHistory.objects.all().order_by("-verified_on")

    return render(
        request,
        "verification_history.html",
        {
            "history": history
        }
    )

# ==========================
# Contact
# ==========================

# ==========================
# Verification Result
# ==========================

def verification_result(request):
    return render(request, "verification_result.html")


def contact(request):
    if request.method == "POST":
        try:
            name = request.POST.get("name")
            email = request.POST.get("email")
            message = request.POST.get("message")
            
            Contact.objects.create(
                name=name,
                email=email,
                message=message
            )
            
            return JsonResponse({"success": True, "message": "Message sent successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)
    
    return render(request, "contact.html")


# ==========================
# User Logout
# ==========================

def user_logout(request):

    request.session.flush()

    return redirect("home")


# ==========================
# Admin Logout
# ==========================

def admin_logout(request):

    request.session.flush()

    return redirect("home")