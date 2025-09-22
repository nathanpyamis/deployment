def scan_documents_for_eligibility(application):
    summary = []
    eligibility_flags = []
    score = 0
    criteria_met = 0

    document_fields = [
        ('transcript', application.transcript),
        ('grade_12_certificate', application.grade_12_certificate),
        ('acceptance_letter', application.acceptance_letter),
        ('school_fee_structure', application.school_fee_structure),
        ('id_card', application.id_card),
        ('character_reference_1', application.character_reference_1),
        ('character_reference_2', application.character_reference_2),
        ('expression_of_interest', application.expression_of_interest),  # ✅ New field
    ]

    for label, file in document_fields:
        if not file:
            eligibility_flags.append(f"❌ Missing: {label.replace('_', ' ').title()}")
            continue

        text = ""
        file_name = file.name.lower()

        try:
            if file_name.endswith('.pdf'):
                with fitz.open(file.path) as pdf:
                    for page in pdf:
                        text += page.get_text()
            elif file_name.endswith(('.png', '.jpg', '.jpeg')):
                image = Image.open(file.path)
                text = pytesseract.image_to_string(image)
        except Exception as e:
            summary.append(f"⚠️ Error reading {label}: {str(e)}")
            continue

        text_lower = text.lower()

        # Eligibility checks
        if label == 'transcript':
            summary.append("Transcript found.")
            if "gpa" in text_lower:
                gpa = extract_gpa(text)
                summary.append(f"GPA detected: {gpa}")
                if gpa >= 3.0:
                    eligibility_flags.append("✅ GPA meets requirement")
                    score += 2
                    criteria_met += 1
                else:
                    eligibility_flags.append("⚠️ GPA below threshold")
            else:
                eligibility_flags.append("⚠️ GPA not found in transcript")

        elif label == 'grade_12_certificate':
            summary.append("Grade 12 Certificate detected.")
            eligibility_flags.append("✅ Academic qualification confirmed")
            score += 1
            criteria_met += 1

        elif label == 'acceptance_letter':
            summary.append("Enrollment proof detected.")
            eligibility_flags.append("✅ Enrollment confirmed")
            score += 1
            criteria_met += 1

        elif label == 'school_fee_structure':
            summary.append("School Fee Structure detected.")
            eligibility_flags.append("✅ Financial need document present")
            score += 1
            criteria_met += 1

        elif label == 'id_card':
            summary.append("ID document detected.")
            eligibility_flags.append("✅ ID verified")
            score += 1
            criteria_met += 1

        elif label.startswith('character_reference'):
            summary.append(f"{label.replace('_', ' ').title()} detected.")
            if "contact" in text_lower or "phone" in text_lower:
                eligibility_flags.append("✅ Reference includes contact info")
                score += 1
                criteria_met += 1
            else:
                eligibility_flags.append("⚠️ Reference missing contact info")

        elif label == 'expression_of_interest':
            summary.append("Expression of Interest Letter detected.")
            if any(keyword in text_lower for keyword in ['motivation', 'interest', 'purpose', 'goal']):
                eligibility_flags.append("✅ Expression of interest contains motivation keywords")
                score += 1
                criteria_met += 1
            else:
                eligibility_flags.append("⚠️ Expression of interest lacks clear motivation")

    summary.append(f"\n📊 Eligibility Score: {score}/8")
    summary.append(f"✅ Criteria Met: {criteria_met}/8")
    summary.append("📌 Flags:")
    summary.extend(eligibility_flags)

    return "\n".join(summary)
