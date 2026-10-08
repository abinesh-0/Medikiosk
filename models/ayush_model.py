from datetime import datetime

from extensions import db


class AyushHistory(db.Model):
    __tablename__ = "ayush_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    prakriti = db.Column(db.Text)
    vikriti = db.Column(db.Text)
    sara = db.Column(db.Text)
    samhanana = db.Column(db.Text)
    pramana = db.Column(db.Text)
    satmya = db.Column(db.Text)
    sattva = db.Column(db.Text)
    ahara_shakti = db.Column(db.Text)
    vyayama_shakti = db.Column(db.Text)
    vaya = db.Column(db.Text)

    ahara_vihara = db.Column(db.Text)
    nidana = db.Column(db.Text)
    samprapti = db.Column(db.Text)
    agni = db.Column(db.Text)
    koshtha = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    case = db.relationship(
        "Case",
        back_populates="ayush_history"
    )

    def to_dict(self):
        return {
            "prakriti": self.prakriti,
            "vikriti": self.vikriti,
            "sara": self.sara,
            "samhanana": self.samhanana,
            "pramana": self.pramana,
            "satmya": self.satmya,
            "sattva": self.sattva,
            "ahara_shakti": self.ahara_shakti,
            "vyayama_shakti": self.vyayama_shakti,
            "vaya": self.vaya,
            "ahara_vihara": self.ahara_vihara,
            "nidana": self.nidana,
            "samprapti": self.samprapti,
            "agni": self.agni,
            "koshtha": self.koshtha,
        }