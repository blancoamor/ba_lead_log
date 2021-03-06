from openerp import models, fields, api
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _

AVAILABLE_EVENT = [
        ('asignation','Asignacion'),
        ('change state','Cambio de estado'),
        ('call','Llamada'),
        ('creation','Creacion'),
    ]



class crm_lead_log(osv.osv):
    _name = "crm.lead.log"
    _description = "log for lead"

    _columns = {
        'name': fields.char('name'),
        'stage_id': fields.many2one('crm.case.stage','state'),
        'lead_id': fields.many2one('crm.lead', 'Lead'),
        'action_type': fields.selection(AVAILABLE_EVENT, 'Action Type'),

    }
    _defaults = {}

crm_lead_log()


class crm_lead(osv.osv):

    def mark_as_spam(self, cr, uid, ids, context=None):
        #stage_id
        vals={'active':False}
        return self.write( cr, uid, ids, vals, context=context)

    def not_is_spam(self, cr, uid, ids, context=None):
        #stage_id
        vals={'active':True}
        return self.write( cr, uid, ids, vals, context=context)

    _inherit = "crm.lead"

    _columns = {}


    def create(self, cr, uid, vals, context=None):
        new_id = super(crm_lead, self).create(cr, uid, vals, context)
        
        crm_lead_log=self.pool.get('crm.lead.log')
        crm_lead_log_vals={}

        if 'stage_id' in vals :
            crm_lead_log_vals['stage_id']=vals['stage_id'];
        crm_lead_log_vals['lead_id']=new_id;
        crm_lead_log_vals['name']='Creacion'
        crm_lead_log_vals['action_type']='creation'            
        crm_lead_log.create(cr, uid,crm_lead_log_vals,context=None)

        return new_id


    def write(self, cr, uid, ids, vals, context=None):
        crm_lead_log=self.pool.get('crm.lead.log')
        crm_lead_log_vals={}

        if 'stage_id' in vals :
            crm_lead_log_vals['stage_id']=vals['stage_id'];
            crm_lead_log_vals['lead_id']=ids[0];
            crm_lead_log_vals['name']='Cambio de Estado'
            crm_lead_log_vals['action_type']='change state'            
            crm_lead_log.create(cr, uid,crm_lead_log_vals,context=None)

        if 'user_id' in vals :
            crm_lead_log_vals['lead_id']=ids[0];
            crm_lead_log_vals['name']='Asignacion'
            crm_lead_log_vals['action_type']='asignation'            
            crm_lead_log.create(cr, uid,crm_lead_log_vals,context=None)


        return super(crm_lead, self).write(cr, uid, ids, vals, context=context)


crm_lead()


class crm_phonecall(osv.osv):
    _inherit = "crm.phonecall"

    _columns = {}


    def create(self, cr, uid, vals, context=None):
        new_id = super(crm_phonecall, self).create(cr, uid, vals, context)
        
        crm_lead_log=self.pool.get('crm.lead.log')
        crm_lead_log_vals={}

        if 'opportunity_id' in vals :
            crm_lead_log_vals['lead_id']=vals['opportunity_id'];
            crm_lead_log_vals['name']='Llamada'
            crm_lead_log_vals['action_type']='call'            
            crm_lead_log.create(cr, uid,crm_lead_log_vals,context=None)
        return new_id

crm_phonecall()


class view_crm_lead_timeline(osv.osv):


    _name = "view.crm.lead.timeline"


    _description = "lead timeline"
    _auto = False
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'lead_id': fields.many2one('crm.lead', 'Lead'),
        'creation_date': fields.datetime( 'creation date'),
        'source_id': fields.many2one('crm.tracking.source', 'Source', help="This is the source of the link Ex: Search Engine, another domain, or name of email list"),
        'asignation_date': fields.datetime( 'asignation date'),
        'call_date': fields.datetime( 'call date'),
        'close_date': fields.datetime( 'close date'),
        'goal_date': fields.datetime( 'goal date'),
        'to_asignation_days': fields.float( 'asignation days',group_operator="avg"),
        'to_call_days': fields.float( 'call days',group_operator="avg"),
        'to_close_days': fields.float( 'close days',group_operator="avg"),
        'to_goal_days': fields.float( 'goal days',group_operator="avg"),
        'user_id': fields.many2one('res.users', 'user'),

    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'view_crm_lead_timeline')

        cr.execute("""create or replace view  view_crm_lead_timeline as (
        select  creation.lead_id as id,  creation.lead_id , creation.write_date as creation_date,crm_lead.source_id as source_id, 
        asig.write_date as asignation_date , 
        call.write_date as call_date, close.write_date as close_date, goal.write_date as goal_date, 
        DATE_PART('day',asig.write_date::timestamp-creation.write_date::timestamp) as to_asignation_days ,
        DATE_PART('day',call.write_date::timestamp-creation.write_date::timestamp) as to_call_days ,
        DATE_PART('day',close.write_date::timestamp-creation.write_date::timestamp) as to_close_days ,
        DATE_PART('day',goal.write_date::timestamp-creation.write_date::timestamp) as to_goal_days ,
        crm_lead.user_id

        from crm_lead_log creation 
        left join crm_lead_log asig on (creation.lead_id = asig.lead_id and asig.action_type='asignation') 
        left join crm_lead_log call on (creation.lead_id = call.lead_id and call.action_type='call') 
        left join crm_lead_log close on (creation.lead_id = close.lead_id and close.action_type='change state' and close.stage_id=7) 
        left join crm_lead_log goal on (creation.lead_id = goal.lead_id and goal.action_type='change state' and goal.stage_id=6) 
        left join crm_lead as crm_lead on (crm_lead.id=creation.lead_id)

        where creation.action_type='creation' and crm_lead.active=True)""")

class view_crm_lead_gestion(osv.osv):


    _name = "view.crm.lead.gestion"


    _description = "gestion de leads"
    _auto = False
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'lead_id': fields.many2one('crm.lead', 'Lead'),
        'creation_date': fields.datetime( 'creation date'),
        'source_id': fields.many2one('crm.tracking.source', 'Source', help="This is the source of the link Ex: Search Engine, another domain, or name of email list"),
        'call_date': fields.datetime( 'call date'),
        'write_date': fields.datetime( 'write_date'),

        'total': fields.float( 'Total',group_operator="sum"),
        'not_active': fields.float( 'Sin Gestionar',group_operator="sum"),
        'day': fields.float( 'Un dia',group_operator="sum"),
        'fweek': fields.float( 'Una Semana',group_operator="sum"),
        'sweek': fields.float( 'Dos Semanas',group_operator="sum"),
        'month': fields.float( 'Un mes',group_operator="sum"),
        'smonth': fields.float( 'Mas de un mes',group_operator="sum"),


        'user_id': fields.many2one('res.users', 'user'),

    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'view_crm_lead_gestion')

        cr.execute("""create or replace view  view_crm_lead_gestion as (
            select creation.lead_id as id,  creation.lead_id , creation.write_date as creation_date,crm_lead.source_id as source_id ,
             change_state.write_date,1 as total,
              DATE_PART('day',creation.write_date::timestamp-change_state.write_date::timestamp) as first_change_days ,

            case when DATE_PART('day',creation.write_date::timestamp-change_state.write_date::timestamp) is Null then 1  else 0 end  as not_active,
            case when DATE_PART('day',creation.write_date::timestamp-change_state.write_date::timestamp) < 2 then 1  else 0 end  as day ,
            case when DATE_PART('day',creation.write_date::timestamp-change_state.write_date::timestamp) BETWEEN 1 and 7 then 1  else 0 end  as fweek,
            case when DATE_PART('day',creation.write_date::timestamp-change_state.write_date::timestamp) BETWEEN 7 and 15 then 1  else 0 end  as sweek,
            case when DATE_PART('day',creation.write_date::timestamp-change_state.write_date::timestamp) BETWEEN 15 and 30 then 1  else 0 end  as month,
            case when DATE_PART('day',creation.write_date::timestamp-change_state.write_date::timestamp) > 30 then 1  else 0 end  as smonth,

            crm_lead.user_id

            from crm_lead_log as creation 
            left join (
                select lead_id , min(write_date) write_date from  crm_lead_log where action_type='change state' group by lead_id
            ) as change_state on (change_state.lead_id=creation.lead_id)
            join crm_lead as crm_lead on (crm_lead.id=creation.lead_id)
            where creation.action_type='creation' and crm_lead.active=True

        )""")


