import json
import os
import sqlite3
from typing import List, Tuple

from covalent._results_manager.result import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.utils import encode_result, get_named_params

# DB Schema:
# TABLE dispatches
# * dispatch_id text primary key
# * result_dict text ; json-serialied dictionary representation of Result

# TODO: Move these to a common utils module

app_log = logger.app_log


class DispatchDB:
    """
    Wrapper for the database of workflows.
    """

    def __init__(self, dbpath: str = None) -> None:
        if dbpath:
            self._dbpath = dbpath
        else:
            self._dbpath = get_config("user_interface.dispatch_db")

        # dispatch_id is the primary key

        # Initialize the db if necessary; sqlite3 raises
        # sqlite3.OperationalError if table already exists.
        self.conn = sqlite3.connect(self._dbpath)
        try:
            self.conn.execute(
                "CREATE TABLE dispatches \
                (dispatch_id text primary key, \
                result_dict text)"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass
        app_log.debug("Instantiated DispatchDB")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

        return False

    def get(self, dispatch_ids: [] = []) -> List[Tuple[str, str]]:
        """
        Retrieve workflows with the given dispatch ids.

        Args:
            dispatch_ids: A list of dispatch ids for the sought-after workflows.

        Returns:
            A list of pairs (dispatch_id, [jsonified result dictionary]).
        """
        if len(dispatch_ids) > 0:
            app_log.debug("DispatchDB.get() is retrieving results for dispatch ids.")
            app_log.debug(dispatch_ids)
            placeholders = "({})".format(", ".join(["?" for i in dispatch_ids]))
            sql = (
                "SELECT * FROM dispatches WHERE \
            dispatch_id in "
                + placeholders
            )

            res = self.conn.execute(sql, dispatch_ids).fetchall()
            app_log.debug("DispatchDB.get() is returning the following response object.")
            app_log.debug(res)

        else:
            sql = "SELECT * FROM dispatches"

            res = self.conn.execute(sql).fetchall()

        return res

    def upsert(self, dispatch_id: str, result_obj: Result) -> None:
        """
        Insert or update the record with the given dispatch_id.

        Args:
            dispatch_id: The workflow's dispatch_id.
            result_obj: The Result object for the workflow.

        The Result is turned into a dictionary and stored as json.
        """

        jsonified_result = encode_result(result_obj)

        try:
            sql = "INSERT INTO dispatches (dispatch_id, result_dict) VALUES (?, ?)"
            self.conn.execute(sql, (dispatch_id, jsonified_result))
            self.conn.commit()

        except sqlite3.IntegrityError:
            sql = "UPDATE dispatches SET result_dict = ? WHERE dispatch_id = ?"
            self.conn.execute(sql, (jsonified_result, dispatch_id))
            self.conn.commit()

        # sql = "INSERT INTO dispatches (dispatch_id, result_dict) VALUES (?, ?) \
        # ON CONFLICT (dispatch_id) DO UPDATE SET result_dict = excluded.result_dict"

        # self.conn.execute(sql, (dispatch_id, jsonified_result))

    def delete(self, dispatch_ids: []) -> None:
        """
        Delete records with the given dispatch ids.

        Args:
            dispatch_ids: A list of dispatch ids
        """
        placeholders = "({})".format(", ".join(["?" for i in dispatch_ids]))
        sql = "DELETE FROM dispatches WHERE dispatch_id in " + placeholders

        self.conn.execute(sql, dispatch_ids)
        self.conn.commit()
