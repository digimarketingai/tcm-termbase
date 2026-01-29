from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Term, Category, Suggestion
from sqlalchemy import or_
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tcm_termbase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables on first request
@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()
    # Check if we need to seed data
    if Term.query.count() == 0:
        seed_database()

def seed_database():
    """Seed the database with initial TCM terms"""
    
    # Create categories
    categories_data = [
        {'name_en': 'Fundamental Theories', 'name_zh': '基础理论', 'description': 'Core concepts of TCM theory'},
        {'name_en': 'Zang-Fu Organs', 'name_zh': '脏腑', 'description': 'Internal organs in TCM'},
        {'name_en': 'Meridians & Acupoints', 'name_zh': '经络腧穴', 'description': 'Channels and acupuncture points'},
        {'name_en': 'Diagnostics', 'name_zh': '诊断', 'description': 'Diagnostic methods and patterns'},
        {'name_en': 'Herbal Medicine', 'name_zh': '中药', 'description': 'Chinese medicinal substances'},
        {'name_en': 'Formulas', 'name_zh': '方剂', 'description': 'Classical and modern prescriptions'},
        {'name_en': 'Treatment Methods', 'name_zh': '治法', 'description': 'Therapeutic principles and techniques'},
        {'name_en': 'Pathology', 'name_zh': '病理', 'description': 'Disease mechanisms and patterns'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        cat = Category(**cat_data)
        db.session.add(cat)
        categories[cat_data['name_en']] = cat
    
    db.session.commit()
    
    # Create sample terms
    terms_data = [
        # Fundamental Theories
        {
            'chinese_simplified': '阴阳',
            'chinese_traditional': '陰陽',
            'pinyin': 'yīn yáng',
            'english_term': 'Yin and Yang',
            'english_aliases': 'Yin-Yang, Yin & Yang',
            'definition_en': 'The fundamental concept in TCM representing two opposite yet complementary forces that exist in all aspects of life and the universe. Yin represents the passive, cold, dark, and interior aspects, while Yang represents the active, warm, bright, and exterior aspects.',
            'definition_zh': '中医学的基本概念，代表宇宙和生命中两种相反而又互补的力量。阴代表被动、寒冷、黑暗和内在的方面，而阳代表主动、温暖、明亮和外在的方面。',
            'etymology': 'Originally referred to the shady and sunny sides of a hill.',
            'category': 'Fundamental Theories',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '气',
            'chinese_traditional': '氣',
            'pinyin': 'qì',
            'english_term': 'Qi',
            'english_aliases': 'Chi, Ki, Vital Energy, Life Force',
            'definition_en': 'The vital substance that constitutes the human body and maintains life activities. It is the fundamental substance that constitutes the universe and produces everything through its movement and changes.',
            'definition_zh': '构成人体和维持生命活动的基本物质。是构成宇宙的基本物质，通过其运动和变化产生万物。',
            'etymology': 'The character originally depicted steam rising from cooking rice.',
            'clinical_notes': 'Qi deficiency is one of the most common patterns seen in clinical practice.',
            'category': 'Fundamental Theories',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '血',
            'chinese_traditional': '血',
            'pinyin': 'xuè',
            'english_term': 'Blood',
            'english_aliases': 'Xue',
            'definition_en': 'One of the vital substances in TCM, red liquid circulating in the vessels that nourishes and moistens the entire body. TCM Blood is broader than the biomedical concept, including nutritive and functional aspects.',
            'definition_zh': '中医基本物质之一，运行于脉中的红色液体，具有营养和滋润全身的作用。中医的血概念比西医更广泛，包含营养和功能方面。',
            'category': 'Fundamental Theories',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '津液',
            'chinese_traditional': '津液',
            'pinyin': 'jīn yè',
            'english_term': 'Body Fluids',
            'english_aliases': 'Jin-Ye,津液',
            'definition_en': 'A general term for all normal fluids in the body. Jin refers to thin, clear fluids that circulate with Qi and moisten the skin and muscles. Ye refers to thick, turbid fluids that nourish the joints, brain, and marrow.',
            'definition_zh': '人体内一切正常水液的总称。津指清稀的液体，随气运行，滋润肌肤；液指稠厚的液体，濡养关节、脑髓。',
            'category': 'Fundamental Theories',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '精',
            'chinese_traditional': '精',
            'pinyin': 'jīng',
            'english_term': 'Essence',
            'english_aliases': 'Jing, Essential Qi',
            'definition_en': 'The most fundamental vital substance, stored in the Kidney, that underlies all organic life. It includes congenital essence (inherited from parents) and acquired essence (derived from food).',
            'definition_zh': '最基本的生命物质，藏于肾，是有机生命的根本。包括先天之精（遗传自父母）和后天之精（来源于食物）。',
            'category': 'Fundamental Theories',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '神',
            'chinese_traditional': '神',
            'pinyin': 'shén',
            'english_term': 'Spirit',
            'english_aliases': 'Shen, Mind, Vitality',
            'definition_en': 'In a broad sense, the outward manifestation of vital activities. In a narrow sense, mental and emotional activities including consciousness, thinking, and emotions, housed in the Heart.',
            'definition_zh': '广义指生命活动的外在表现；狭义指精神、意识、思维活动，藏于心。',
            'category': 'Fundamental Theories',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '五行',
            'chinese_traditional': '五行',
            'pinyin': 'wǔ xíng',
            'english_term': 'Five Phases',
            'english_aliases': 'Five Elements, Wu Xing',
            'definition_en': 'A system of correspondences used in TCM to explain physiological and pathological phenomena. The five phases are Wood, Fire, Earth, Metal, and Water, each with specific characteristics and relationships.',
            'definition_zh': '中医用以解释生理和病理现象的对应系统。五行为木、火、土、金、水，各有特定的特性和相互关系。',
            'category': 'Fundamental Theories',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        
        # Zang-Fu Organs
        {
            'chinese_simplified': '心',
            'chinese_traditional': '心',
            'pinyin': 'xīn',
            'english_term': 'Heart',
            'english_aliases': 'Heart System',
            'definition_en': 'One of the five Zang organs. It governs blood and vessels, houses the Shen (spirit/mind), manifests in the complexion, opens to the tongue, and controls sweat.',
            'definition_zh': '五脏之一。主血脉，藏神，其华在面，开窍于舌，在液为汗。',
            'clinical_notes': 'Heart patterns often involve palpitations, insomnia, anxiety, and tongue changes.',
            'category': 'Zang-Fu Organs',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '肝',
            'chinese_traditional': '肝',
            'pinyin': 'gān',
            'english_term': 'Liver',
            'english_aliases': 'Liver System',
            'definition_en': 'One of the five Zang organs. It stores blood, ensures smooth flow of Qi, controls the sinews, manifests in the nails, and opens to the eyes.',
            'definition_zh': '五脏之一。藏血，主疏泄，主筋，其华在爪，开窍于目。',
            'clinical_notes': 'Liver patterns often involve emotional disturbance, eye problems, and tendon issues.',
            'category': 'Zang-Fu Organs',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '脾',
            'chinese_traditional': '脾',
            'pinyin': 'pí',
            'english_term': 'Spleen',
            'english_aliases': 'Spleen System',
            'definition_en': 'One of the five Zang organs. It governs transformation and transportation, controls blood, dominates the muscles and limbs, manifests in the lips, and opens to the mouth.',
            'definition_zh': '五脏之一。主运化，统血，主肌肉四肢，其华在唇，开窍于口。',
            'clinical_notes': 'Spleen patterns often involve digestive issues, fatigue, and bleeding disorders.',
            'category': 'Zang-Fu Organs',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '肺',
            'chinese_traditional': '肺',
            'pinyin': 'fèi',
            'english_term': 'Lung',
            'english_aliases': 'Lung System',
            'definition_en': 'One of the five Zang organs. It governs Qi and respiration, controls dispersing and descending, regulates water passages, controls the skin and body hair, and opens to the nose.',
            'definition_zh': '五脏之一。主气司呼吸，主宣发肃降，通调水道，主皮毛，开窍于鼻。',
            'clinical_notes': 'Lung patterns often involve respiratory issues, skin problems, and immune weakness.',
            'category': 'Zang-Fu Organs',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '肾',
            'chinese_traditional': '腎',
            'pinyin': 'shèn',
            'english_term': 'Kidney',
            'english_aliases': 'Kidney System',
            'definition_en': 'One of the five Zang organs. It stores essence, governs water metabolism, receives Qi, controls bones and marrow, manifests in the hair, and opens to the ears and two lower orifices.',
            'definition_zh': '五脏之一。藏精，主水，纳气，主骨生髓，其华在发，开窍于耳及二阴。',
            'clinical_notes': 'Kidney patterns often involve reproductive issues, bone problems, hearing loss, and aging.',
            'category': 'Zang-Fu Organs',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        
        # Meridians & Acupoints
        {
            'chinese_simplified': '经络',
            'chinese_traditional': '經絡',
            'pinyin': 'jīng luò',
            'english_term': 'Meridians and Collaterals',
            'english_aliases': 'Channels, Jing-Luo',
            'definition_en': 'The network of pathways through which Qi and Blood circulate throughout the body, connecting the interior with the exterior and the upper with the lower body.',
            'definition_zh': '气血运行的通道网络，贯通上下内外，联系脏腑肢节。',
            'category': 'Meridians & Acupoints',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '穴位',
            'chinese_traditional': '穴位',
            'pinyin': 'xué wèi',
            'english_term': 'Acupoint',
            'english_aliases': 'Acupuncture Point, Point',
            'definition_en': 'Specific locations on the body surface where Qi and Blood of the meridians infuse and transmit. These points are used for acupuncture, moxibustion, and massage therapy.',
            'definition_zh': '经络之气输注于体表的特定部位，是针灸、艾灸、按摩治疗的刺激点。',
            'category': 'Meridians & Acupoints',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '足三里',
            'chinese_traditional': '足三里',
            'pinyin': 'zú sān lǐ',
            'english_term': 'Zusanli (ST36)',
            'english_aliases': 'ST36, Stomach 36, Three Miles of the Leg',
            'definition_en': 'An important acupoint on the Stomach meridian, located 3 cun below the knee. It tonifies Qi and Blood, harmonizes the Stomach, and strengthens the body.',
            'definition_zh': '足阳明胃经重要穴位，位于膝下三寸。功能补益气血，和胃健脾，强身健体。',
            'clinical_notes': 'One of the most frequently used points for general tonification and digestive issues.',
            'category': 'Meridians & Acupoints',
            'who_standard': True,
            'source': 'WHO Standard Acupuncture Point Locations',
            'reliability_score': 5
        },
        
        # Diagnostics
        {
            'chinese_simplified': '望诊',
            'chinese_traditional': '望診',
            'pinyin': 'wàng zhěn',
            'english_term': 'Inspection',
            'english_aliases': 'Visual Examination, Observation',
            'definition_en': 'One of the four diagnostic methods in TCM, involving visual observation of the patient\'s spirit, complexion, body shape, posture, tongue, and excreta.',
            'definition_zh': '中医四诊之一，通过观察病人的神、色、形、态、舌象、排泄物等进行诊断。',
            'category': 'Diagnostics',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '舌诊',
            'chinese_traditional': '舌診',
            'pinyin': 'shé zhěn',
            'english_term': 'Tongue Diagnosis',
            'english_aliases': 'Tongue Examination',
            'definition_en': 'A diagnostic method examining the tongue body (shape, color, moisture) and tongue coating (color, thickness, distribution) to assess the condition of the internal organs and pathogenic factors.',
            'definition_zh': '通过观察舌体（形状、颜色、润燥）和舌苔（颜色、厚薄、分布）来判断脏腑病变和病邪性质的诊断方法。',
            'category': 'Diagnostics',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '脉诊',
            'chinese_traditional': '脈診',
            'pinyin': 'mài zhěn',
            'english_term': 'Pulse Diagnosis',
            'english_aliases': 'Pulse Examination, Pulse Taking',
            'definition_en': 'A diagnostic method of feeling the pulse at the radial artery to assess the condition of Qi, Blood, Yin, Yang, and the internal organs. Traditional TCM recognizes 28 classic pulse types.',
            'definition_zh': '在桡动脉处切脉以判断气血阴阳和脏腑状态的诊断方法。传统中医有二十八种脉象。',
            'category': 'Diagnostics',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '辨证论治',
            'chinese_traditional': '辨證論治',
            'pinyin': 'biàn zhèng lùn zhì',
            'english_term': 'Pattern Identification and Treatment',
            'english_aliases': 'Syndrome Differentiation and Treatment, Bian Zheng Lun Zhi',
            'definition_en': 'The fundamental principle of TCM diagnosis and treatment, involving analyzing symptoms to identify the underlying pattern (zheng) and then determining the appropriate treatment strategy.',
            'definition_zh': '中医诊治的基本原则，通过分析症状辨别证候，进而确定治疗方案。',
            'category': 'Diagnostics',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        
        # Pathology
        {
            'chinese_simplified': '气虚',
            'chinese_traditional': '氣虛',
            'pinyin': 'qì xū',
            'english_term': 'Qi Deficiency',
            'english_aliases': 'Qi Xu, Deficient Qi',
            'definition_en': 'A pattern characterized by insufficient Qi, manifesting as fatigue, weakness, shortness of breath, spontaneous sweating, pale tongue, and weak pulse.',
            'definition_zh': '气不足的证候，表现为疲乏无力、气短懒言、自汗、舌淡、脉弱。',
            'clinical_notes': 'Common in chronic illness, overwork, and aging. Often treated with Qi-tonifying herbs.',
            'category': 'Pathology',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '血瘀',
            'chinese_traditional': '血瘀',
            'pinyin': 'xuè yū',
            'english_term': 'Blood Stasis',
            'english_aliases': 'Blood Stagnation, Xue Yu',
            'definition_en': 'A pathological condition where blood circulation is impaired, causing fixed stabbing pain, dark complexion, purple tongue with spots, and choppy pulse.',
            'definition_zh': '血液运行不畅的病理状态，表现为刺痛固定、面色晦暗、舌紫有瘀斑、脉涩。',
            'clinical_notes': 'Common in trauma, chronic pain conditions, and cardiovascular diseases.',
            'category': 'Pathology',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '痰湿',
            'chinese_traditional': '痰濕',
            'pinyin': 'tán shī',
            'english_term': 'Phlegm-Dampness',
            'english_aliases': 'Phlegm and Dampness, Tan Shi',
            'definition_en': 'A pathological pattern characterized by accumulation of phlegm and dampness, manifesting as heaviness, fullness, nausea, excessive mucus, greasy tongue coating, and slippery pulse.',
            'definition_zh': '痰湿内蕴的病理状态，表现为身重、胸闷、恶心、痰多、舌苔腻、脉滑。',
            'clinical_notes': 'Common in obesity, metabolic syndrome, and respiratory conditions.',
            'category': 'Pathology',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        
        # Herbal Medicine
        {
            'chinese_simplified': '人参',
            'chinese_traditional': '人參',
            'pinyin': 'rén shēn',
            'english_term': 'Ginseng',
            'english_aliases': 'Radix Ginseng, Panax Ginseng, Ren Shen',
            'definition_en': 'The root of Panax ginseng. It powerfully tonifies Yuan Qi, strengthens the Spleen and Lung, generates fluids, and calms the spirit. One of the most important Qi-tonifying herbs.',
            'definition_zh': '五加科植物人参的根。功能大补元气，补脾益肺，生津止渴，安神益智。为补气要药。',
            'clinical_notes': 'Contraindicated in heat patterns and hypertension. May interact with anticoagulants.',
            'category': 'Herbal Medicine',
            'subcategory': 'Qi-Tonifying Herbs',
            'who_standard': True,
            'source': 'Chinese Pharmacopoeia',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '黄芪',
            'chinese_traditional': '黃芪',
            'pinyin': 'huáng qí',
            'english_term': 'Astragalus Root',
            'english_aliases': 'Radix Astragali, Huang Qi, Milkvetch Root',
            'definition_en': 'The root of Astragalus membranaceus. It tonifies Qi, raises Yang, consolidates the exterior, promotes urination, and generates flesh. Commonly used for immune support.',
            'definition_zh': '豆科植物黄芪的根。功能补气升阳，固表止汗，利水消肿，托毒生肌。常用于提高免疫力。',
            'clinical_notes': 'One of the most commonly used herbs in modern clinical practice for immune support.',
            'category': 'Herbal Medicine',
            'subcategory': 'Qi-Tonifying Herbs',
            'who_standard': True,
            'source': 'Chinese Pharmacopoeia',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '当归',
            'chinese_traditional': '當歸',
            'pinyin': 'dāng guī',
            'english_term': 'Chinese Angelica Root',
            'english_aliases': 'Radix Angelicae Sinensis, Dang Gui, Dong Quai',
            'definition_en': 'The root of Angelica sinensis. It tonifies and invigorates blood, regulates menstruation, relieves pain, and moistens the intestines. The primary herb for blood disorders.',
            'definition_zh': '伞形科植物当归的根。功能补血活血，调经止痛，润肠通便。为补血调经要药。',
            'clinical_notes': 'Essential herb for gynecological conditions. May potentiate anticoagulant effects.',
            'category': 'Herbal Medicine',
            'subcategory': 'Blood-Tonifying Herbs',
            'who_standard': True,
            'source': 'Chinese Pharmacopoeia',
            'reliability_score': 5
        },
        
        # Formulas
        {
            'chinese_simplified': '四君子汤',
            'chinese_traditional': '四君子湯',
            'pinyin': 'sì jūn zǐ tāng',
            'english_term': 'Four Gentlemen Decoction',
            'english_aliases': 'Si Jun Zi Tang',
            'definition_en': 'A classical formula for Qi deficiency, containing Ren Shen, Bai Zhu, Fu Ling, and Zhi Gan Cao. It tonifies Qi and strengthens the Spleen. The foundation for many Qi-tonifying formulas.',
            'definition_zh': '治疗气虚的经典方剂，由人参、白术、茯苓、炙甘草组成。功能益气健脾。为补气方剂的基础方。',
            'clinical_notes': 'Often modified by adding herbs for specific conditions.',
            'category': 'Formulas',
            'subcategory': 'Qi-Tonifying Formulas',
            'who_standard': False,
            'source': 'Taiping Huimin Heji Jufang (太平惠民和剂局方)',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '四物汤',
            'chinese_traditional': '四物湯',
            'pinyin': 'sì wù tāng',
            'english_term': 'Four Substances Decoction',
            'english_aliases': 'Si Wu Tang',
            'definition_en': 'A classical formula for blood deficiency, containing Shu Di Huang, Dang Gui, Bai Shao, and Chuan Xiong. It tonifies and regulates blood. The foundation for blood-nourishing formulas.',
            'definition_zh': '治疗血虚的经典方剂，由熟地黄、当归、白芍、川芎组成。功能补血调血。为补血方剂的基础方。',
            'clinical_notes': 'Frequently combined with Si Jun Zi Tang (Ba Zhen Tang) for Qi and Blood deficiency.',
            'category': 'Formulas',
            'subcategory': 'Blood-Tonifying Formulas',
            'who_standard': False,
            'source': 'Taiping Huimin Heji Jufang (太平惠民和剂局方)',
            'reliability_score': 5
        },
        
        # Treatment Methods
        {
            'chinese_simplified': '针灸',
            'chinese_traditional': '針灸',
            'pinyin': 'zhēn jiǔ',
            'english_term': 'Acupuncture and Moxibustion',
            'english_aliases': 'Zhen Jiu',
            'definition_en': 'A therapeutic method using needles (acupuncture) and burning moxa (moxibustion) to stimulate specific points on the body to regulate Qi and Blood flow.',
            'definition_zh': '使用针刺和艾灸刺激体表特定穴位以调节气血的治疗方法。',
            'category': 'Treatment Methods',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '推拿',
            'chinese_traditional': '推拿',
            'pinyin': 'tuī ná',
            'english_term': 'Tuina Massage',
            'english_aliases': 'Tui Na, Chinese Therapeutic Massage',
            'definition_en': 'A therapeutic massage technique using various hand techniques to stimulate acupoints and meridians, regulate Qi and Blood, and treat musculoskeletal and internal disorders.',
            'definition_zh': '运用各种手法刺激穴位经络，调节气血，治疗筋骨和内科疾病的按摩疗法。',
            'category': 'Treatment Methods',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
        {
            'chinese_simplified': '拔罐',
            'chinese_traditional': '拔罐',
            'pinyin': 'bá guàn',
            'english_term': 'Cupping Therapy',
            'english_aliases': 'Cupping, Ba Guan',
            'definition_en': 'A therapeutic technique using suction cups on the skin to promote blood circulation, remove blood stasis, and expel pathogenic factors.',
            'definition_zh': '利用罐具吸附于皮肤以促进血液循环、消除瘀血、祛除病邪的治疗方法。',
            'category': 'Treatment Methods',
            'who_standard': True,
            'source': 'WHO International Standard Terminologies on Traditional Medicine',
            'reliability_score': 5
        },
    ]
    
    for term_data in terms_data:
        category_name = term_data.pop('category')
        category = categories.get(category_name)
        
        term = Term(**term_data, category_id=category.id if category else None)
        term.update_search_text()
        db.session.add(term)
    
    db.session.commit()

@app.route('/')
def index():
    """Homepage with search and statistics"""
    total_terms = Term.query.count()
    categories = Category.query.all()
    recent_terms = Term.query.order_by(Term.created_at.desc()).limit(10).all()
    return render_template('index.html', 
                         total_terms=total_terms, 
                         categories=categories,
                         recent_terms=recent_terms)

@app.route('/search')
def search():
    """Full-text search across all fields"""
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if not query:
        return render_template('search.html', terms=[], query='', categories=Category.query.all())
    
    # Build search query
    search_term = f'%{query.lower()}%'
    
    terms_query = Term.query.filter(
        or_(
            Term.search_text.ilike(search_term),
            Term.chinese_simplified.ilike(search_term),
            Term.chinese_traditional.ilike(search_term),
            Term.pinyin.ilike(search_term),
            Term.english_term.ilike(search_term),
            Term.english_aliases.ilike(search_term)
        )
    )
    
    if category_id:
        terms_query = terms_query.filter(Term.category_id == category_id)
    
    pagination = terms_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('search.html', 
                         terms=pagination.items, 
                         pagination=pagination,
                         query=query,
                         category_id=category_id,
                         categories=Category.query.all())

@app.route('/term/<int:term_id>')
def term_detail(term_id):
    """Display detailed information for a single term"""
    term = Term.query.get_or_404(term_id)
    related_terms = Term.query.filter(
        Term.category_id == term.category_id,
        Term.id != term.id
    ).limit(5).all()
    return render_template('term_detail.html', term=term, related_terms=related_terms)

@app.route('/browse')
def browse():
    """Browse terms by category"""
    category_id = request.args.get('category', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    categories = Category.query.all()
    
    if category_id:
        terms_query = Term.query.filter_by(category_id=category_id)
        current_category = Category.query.get(category_id)
    else:
        terms_query = Term.query
        current_category = None
    
    terms_query = terms_query.order_by(Term.pinyin)
    pagination = terms_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('browse.html',
                         terms=pagination.items,
                         pagination=pagination,
                         categories=categories,
                         current_category=current_category,
                         category_id=category_id)

@app.route('/contribute', methods=['GET', 'POST'])
def contribute():
    """Allow users to suggest new terms or corrections"""
    if request.method == 'POST':
        suggestion = Suggestion(
            term_id=request.form.get('term_id', type=int),
            suggestion_type=request.form.get('suggestion_type'),
            content=request.form.get('content'),
            submitter_email=request.form.get('email'),
            submitter_name=request.form.get('name')
        )
        db.session.add(suggestion)
        db.session.commit()
        return render_template('contribute.html', success=True)
    
    return render_template('contribute.html', success=False)

@app.route('/about')
def about():
    """About page with information about the termbase"""
    return render_template('about.html')

@app.route('/api/search')
def api_search():
    """API endpoint for search (for AJAX requests)"""
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)
    
    if not query or len(query) < 2:
        return jsonify([])
    
    search_term = f'%{query.lower()}%'
    
    terms = Term.query.filter(
        or_(
            Term.chinese_simplified.ilike(search_term),
            Term.chinese_traditional.ilike(search_term),
            Term.pinyin.ilike(search_term),
            Term.english_term.ilike(search_term)
        )
    ).limit(limit).all()
    
    results = [{
        'id': t.id,
        'chinese_simplified': t.chinese_simplified,
        'pinyin': t.pinyin,
        'english_term': t.english_term
    } for t in terms]
    
    return jsonify(results)

@app.route('/api/term/<int:term_id>')
def api_term(term_id):
    """API endpoint for single term data"""
    term = Term.query.get_or_404(term_id)
    return jsonify({
        'id': term.id,
        'chinese_simplified': term.chinese_simplified,
        'chinese_traditional': term.chinese_traditional,
        'pinyin': term.pinyin,
        'english_term': term.english_term,
        'english_aliases': term.english_aliases,
        'definition_en': term.definition_en,
        'definition_zh': term.definition_zh,
        'etymology': term.etymology,
        'clinical_notes': term.clinical_notes,
        'category': term.category.name_en if term.category else None,
        'source': term.source,
        'who_standard': term.who_standard
    })

if __name__ == '__main__':
    app.run(debug=True)
