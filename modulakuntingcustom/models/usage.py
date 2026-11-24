# -*- coding: utf-8 -*-
from odoo import models, fields, api
import psycopg2
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class Usage(models.Model):
    _name = 'modulakuntingcustom.usage'
    _description = 'Usage'

    username = fields.Char(string='Username')
    upload = fields.Char(string='Upload')
    download = fields.Char(string='Download')
    usage = fields.Char(string='Usage')
    date_in = fields.Char(string='Date In')
    date_out = fields.Char(string='Date Out')

    @api.model
    def fetch_data_from_postgres(self):
        try:
            conn = psycopg2.connect(
                dbname="freeradius",
                user="posta17",
                password="r4h4s14k4n",
                host="192.168.10.9",
                port="5432"
            )
            cursor = conn.cursor()
            _logger.info("Connection to PostgreSQL successful.")

            # Query 6 bulan terakhir
            query = """
                SELECT username, acctstarttime, acctupdatetime, acctstoptime,
                       acctinputoctets, acctoutputoctets
                FROM radacct
                WHERE COALESCE(acctupdatetime, acctstarttime) 
                      AT TIME ZONE 'Asia/Jakarta' >= (NOW() AT TIME ZONE 'Asia/Jakarta') - interval '6 months'
                ORDER BY acctstarttime ASC;
            """
            cursor.execute(query)
            results = cursor.fetchall()
            _logger.info("Fetched %s rows from PostgreSQL", len(results))

            # Hapus data lama Odoo
            self.search([]).unlink()

            for row in results:
                username = row[0]
                raw_date_in = row[1]
                raw_date_upd = row[2]
                raw_date_out = row[3]
                upload = row[4] or 0
                download = row[5] or 0

                upload_mbps = int(upload) / 1e+6
                download_mbps = int(download) / 1e+6
                usage_mbps = upload_mbps + download_mbps

                date_in = datetime.fromisoformat(str(raw_date_in)).strftime('%Y-%m-%d %H:%M') if raw_date_in else None
                date_out = datetime.fromisoformat(str(raw_date_out)).strftime('%Y-%m-%d %H:%M') if raw_date_out else None

                self.create({
                    'username': username,
                    'upload': f"{upload_mbps:.2f} Mbps",
                    'download': f"{download_mbps:.2f} Mbps",
                    'usage': f"{usage_mbps:.2f} Mbps",
                    'date_in': date_in,
                    'date_out': date_out,
                })

            _logger.info("Data successfully fetched and updated (last 6 months).")

        except Exception as e:
            _logger.error("Failed to fetch data from PostgreSQL: %s", e)

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()

    def action_sync_data(self):
        self.fetch_data_from_postgres()
