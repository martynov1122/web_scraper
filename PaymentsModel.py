import peewee

database = peewee.SqliteDatabase("FyndiqPayments.db")

class FyndiqPayments(peewee.Model):
    payment_date = peewee.DateTimeField()
    amount = peewee.FloatField()
    final_amount = peewee.FloatField()
    fortnox_id = peewee.IntegerField()
    shopname = peewee.TextField()
    class Meta:
        database = database
