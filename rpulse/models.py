from rpulse import db

class States(db.Model):
    __tablename__ = 'states'
    state_id = db.Column(db.Integer, primary_key=True)
    state_name = db.Column(db.String(30), nullable=False)
    state_abbr = db.Column(db.String(2), nullable=False)
    state_fip = db.Column(db.Integer, nullable=False)
    state_sub = db.Column(db.String(30), nullable=False)
    pop_2018 = db.Column(db.Integer, nullable=False)
    sub_cnt = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"States('{self.state_name}', '{self.state_abbr}', \
                        '{self.state_fip}', '{self.state_sub}', '{self.sub_cnt}, \
                        '{self.pop_2018}')"

class Cities(db.Model):
    __tablename__ = 'cities'
    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(30), nullable=False)
    city_sub = db.Column(db.String(30), nullable=False)
    sub_cnt = db.Column(db.Integer, nullable=False)
    pop_2018 = db.Column(db.Integer, nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey('states.state_id'))

    def __repr__(self):
        return f"Cities('{self.city_id}', '{self.city_name}', '{self.city_sub}', \
                        '{self.sub_cnt}', '{self.state_id}', '{self.pop_2018}')"

class Topics(db.Model):
    __tablename__ = 'topics'
    topic_id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"Topics('{self.topic_id}', '{self.topic}')"

class Keywords(db.Model):
    __tablename__ = 'keywords'
    keyword_id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"Keywords('{self.keyword_id}', '{self.keyword}')"

class Topics_geo(db.Model):
    __tablename__ = 'topics_geo'
    id = db.Column(db.Integer, primary_key=True)
    geo_type = db.Column(db.String(30), nullable=False)
    geo_id = db.Column(db.Integer, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'))

    def __repr__(self):
        return f"Topics_geo('{self.id}', '{self.geo_type}', '{self.geo_id}', \
                        '{self.topic_id}')"

class Topics_keywords(db.Model):
    __tablename__ = 'topics_keywords'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'))
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.keyword_id'))

    def __repr__(self):
        return f"Topics_keywords('{self.id}', '{self.geo_type}', '{self.geo_id}', \
                        '{self.topic_id}')"