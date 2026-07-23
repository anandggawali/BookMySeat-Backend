from core.database import db


class ConfigurationRepository:

    @staticmethod
    def get_version_config():
        return db.configuration.find_one(
            {"configType": "VERSION"},
            {"_id": 0, "configType": 0}
        )

    @staticmethod
    def get_support_config():
        return db.configuration.find_one(
            {"configType": "SUPPORT"},
            {"_id": 0, "configType": 0}
        )

    @staticmethod
    def get_booking_rules():
        return list(
            db.booking_rules.find(
                {"is_active": True},
                {"_id": 0}
            )
        )

    @staticmethod
    def get_reject_reasons():
        return list(
            db.reject_reasons.find(
                {"is_active": True},
                {"_id": 0}
            )
        )