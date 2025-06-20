from app import db


class Stock(db.Model):
    __tablename__ = 'stocks'
    
    ticker = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(255))
    sector = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Stock {self.ticker}>'