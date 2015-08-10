from openerp import models, fields, api
from openerp.osv import fields, osv
from openerp.tools.translate import _

AVAILABLE_EVENT = [
        ('asignation','Asignacion'),
        ('change state','Cambio de estado'),
        ('call','Llamada'),
        ('Creation','Creacion'),
    ]



class crm_lead_log(osv.osv):
    _name = "account.invoice"
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
    _inherit = "crm.lead"

    _columns = {}


    def create(self, cr, uid, vals, context=None):
        new_id = super(crm_lead, self).create(cr, uid, vals, context)
        
        crm_lead_log=self.pool.get('crm.lead.log')
        crm_lead_log_vals={}

        crm_lead_log_vals['stage_id']=stage_id;
        crm_lead_log_vals['lead_id']=new_id;
        crm_lead_log_vals['name']='Creacion'
        crm_lead_log_vals['action_type']='Creation'            
        crm_lead_log.create(cr, uid,crm_lead_log_vals,context=None)

        return new_id


    def write(self, cr, uid, ids, vals, context=None):
        crm_lead_log=self.pool.get('crm.lead.log')
        crm_lead_log_vals={}

        if 'stage_id' in vals :
            crm_lead_log_vals['stage_id']=stage_id;
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


'''
class views_crm_lead_log(osv.osv):


    _name = "view.crm.lead.log"


    _description = "Log de crm"
    _auto = False
    _columns = {
    }




    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'views_crm_lead_log')

        cr.execute(""" 
            create or replace view views_crm_lead_log as (
                        select ai.id,ai.id as invoice_id, ai.partner_id , ai.number , ai.name  ,cl.id as claim_id, cl.name as  crm_claim_name , 
                        '-' as invoice_line_text 
                        from account_invoice ai 
                        left join crm_claim cl on (ai.id=cl.invoice_id) 
            )
        """)
'''
