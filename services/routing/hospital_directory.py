from models.department_model import Department
def active_departments():
    return Department.query.filter_by(is_active=True).order_by(Department.name).all()
