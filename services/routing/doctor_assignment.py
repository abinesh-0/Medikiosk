from models.doctor_model import Doctor
def available_doctor(department_id):
    return Doctor.query.filter_by(department_id=department_id,is_available=True).order_by(Doctor.id).first()
