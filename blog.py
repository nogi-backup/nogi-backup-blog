from random import shuffle

from fire import Fire
from tqdm import tqdm

from nogi import engine, metadata
from nogi.db.nogi_blog_content import NogiBlogContent
from nogi.db.nogi_blog_summary import NogiBlogSummary
from nogi.db.nogi_members import NogiMembers
from nogi.utils.post_extractor import PostExecutor
from nogi.utils.updater import Updater
from nogi.storages.gcs import GCS


class CommandLine:

    def __init__(self) -> None:

        # Blog
        self.blog_content = NogiBlogContent(engine, metadata, role='writer')
        self.blog_summary = NogiBlogSummary(engine, metadata, role='writer')
        self.blog_member = NogiMembers(engine, metadata)

        # GCS
        self.gcs = GCS()

    def check_blog_update(self):
        member_latest_post_tx = self.blog_summary.get_members_latest_post_created_ts()
        members = [x for x in self.blog_member.get_current_members()]
        shuffle(members)
        for member in tqdm(members):
            Updater(
                member=member,
                blog_db=self.blog_summary,
                latest_post_ts=member_latest_post_tx.get(member['id'], 0),
            ).run()

    def crawl_blogs(self, bucket: str = 'nogi-test'):
        for member in tqdm(self.blog_member.get_current_members()):
            PostExecutor(
                member=member,
                summary_db=self.blog_summary,
                content_db=self.blog_content,
                gcs_client=self.gcs,
                bucket=bucket
            ).run()


if __name__ == "__main__":
    Fire(CommandLine)
