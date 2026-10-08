def patient_resource(patient):
    return {"resourceType":"Patient","id":str(patient.id),"identifier":[{"system":"https://healthid.abdm.gov.in","value":patient.abha_id}] if patient.abha_id else [],
            "name":[{"text":patient.full_name}],"telecom":[{"system":"email","value":patient.email}] if patient.email else []}
def case_bundle(patient,case):
    return {"resourceType":"Bundle","type":"collection","entry":[{"resource":patient_resource(patient)},
        {"resource":{"resourceType":"Encounter","id":str(case.visit_id),"status":"in-progress"}}]}
