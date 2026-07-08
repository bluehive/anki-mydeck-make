#!/usr/bin/env python3
"""
Task 1: git_deck.csv generator (updated for visuals)
Generates 50 Git Q&A cards + corresponding minimal illustrations.

- 3 columns: 表面, 裏面, Image
- Style: minimal flat icons, limited 24-color palette
- Reference: assets/images/simple-icon-set.jpg
- Images stored in: assets/images/git-deck/
"""

import csv

# 50 cards (front, back)
cards = [
    # ソース資料 23問
    ("カレントディレクトリに新しくGitリポジトリを作成するコマンドは？", "`git init`"),
    ("URLやパスを指定して、既存のリポジトリをカレントディレクトリにコピーするコマンドは？", "`git clone <url_or_path>`"),
    ("現在のワーキングディレクトリの変更状態（ステータス）を表示するコマンドは？", "`git status`"),
    ("カレントディレクトリのすべての変更を、コミットの準備領域（ステージングエリア）に追加するコマンドは？", "`git add .`"),
    ("追加した変更にメッセージを付けて、ローカルリポジトリに記録するコマンドは？", "`git commit -m \"メッセージ\"`"),
    ("リモートリポジトリの最新の変更を取得し、ローカルに統合（プル）するコマンドは？", "`git pull`"),
    ("ローカルリポジトリで記録した変更を、リモートリポジトリに送信（プッシュ）するコマンドは？", "`git push`"),
    ("Gitのコミットに記録される作者情報として、設定すべき2つの項目は？", "ユーザー名（user.name）とメールアドレス（user.email）"),
    ("Gitのコミットに記録されるデフォルトのユーザー名を設定するコマンドは？", "`git config --global user.name \"名前\"`"),
    ("Gitのコミットに記録されるデフォルトのメールアドレスを設定するコマンドは？", "`git config --global user.email \"メールアドレス\"`"),
    ("`git config --global` コマンドで設定したユーザー名などの情報が保存されるファイルはどこか？", "`~/.gitconfig`"),
    ("現在のローカルリポジトリの状態に、バージョンなどの目印（タグ）をつけるコマンドは？", "`git tag \"バージョンやラベル\"`"),
    ("1つのリポジトリで、複数の作業ディレクトリを競合なく切り出すことができるGitの機能は？", "`git worktree`"),
    ("指定したパスに新しいワークツリーを作成し、同時に新しいブランチを作成してチェックアウトするコマンドは？", "`git worktree add <パス> -b <ブランチ名>`"),
    ("誤コミットを防ぐため、ワークツリーを作成する際に安全な場所はどこか？", "リポジトリ外（隣接ディレクトリなど）に作成するのが安全です"),
    ("現在作成されているワークツリーの一覧を確認するコマンドは？", "`git worktree list`"),
    ("ワークツリーを作成した際、`.gitignore`で除外されているファイル（例: node_modules や .env）はどうなるか？", "新しいワークツリーには含まれません。シンボリックリンクを張るか、個別にインストールする必要があります"),
    ("不要になったワークツリーを削除するコマンドは？", "`git worktree remove <パス>`"),
    ("`git worktree remove` 実行時、未コミットの変更が残っているワークツリーはどうなるか？", "安全装置が働き、デフォルトでは削除されない（エラーで中断される）"),
    ("未コミットの変更があるワークツリーを強制的に削除するオプションは？", "`git worktree remove --force <パス>`（`--force`）"),
    ("ワークツリーのディレクトリを直接削除してしまい、`list` に管理情報が残った場合、それを掃除するコマンドは？", "`git worktree prune`"),
    ("ブランチを削除しようとして拒否される原因のうち、ワークツリーに関連するものは？", "どこかのワークツリーでそのブランチがHEADとして開かれているため"),
    ("同じブランチを2つのワークツリーで同時に開くことはできるか？", "できない（1ブランチ = 1ワークツリーがGitの仕様）"),

    # 一般知識 27問
    ("ワーキングディレクトリとステージングエリアの差分を表示するコマンドは？", "`git diff`"),
    ("ステージングエリアと最新コミットの差分を表示するコマンドは？", "`git diff --staged`（または `--cached`）"),
    ("これまでのコミット履歴を表示するコマンドは？", "`git log`"),
    ("コミット履歴を1行ずつ簡潔に表示するオプションは？", "`git log --oneline`"),
    ("特定のコミットで行われた変更内容を確認するコマンドは？", "`git show <コミットID>`"),
    ("ローカルリポジトリに存在するブランチの一覧を表示するコマンドは？", "`git branch`"),
    ("現在のコミットから新しいブランチを作成するコマンドは？（切り替えはしない）", "`git branch <ブランチ名>`"),
    ("指定したブランチに作業を切り替えるコマンドは？", "`git checkout <ブランチ名>`（または `git switch`）"),
    ("新しいブランチを作成し、同時にそのブランチに切り替えるコマンドは？", "`git checkout -b <ブランチ名>`（または `git switch -c`）"),
    ("指定したブランチの変更を、現在のブランチに統合するコマンドは？", "`git merge <ブランチ名>`"),
    ("マージ済みの不要なブランチを削除するコマンドは？", "`git branch -d <ブランチ名>`"),
    ("まだマージされていないブランチを強制的に削除するコマンドは？", "`git branch -D <ブランチ名>`"),
    ("まだコミットしていないワーキングディレクトリの変更を取り消すコマンドは？", "`git restore <ファイル名>`（または `git checkout -- <ファイル名>`）"),
    ("すでに `git add` したファイルをステージングエリアから取り除く（アンステージする）コマンドは？", "`git restore --staged <ファイル名>`（または `git reset HEAD <ファイル名>`）"),
    ("直前のコミットの内容を修正したり、コミットメッセージを書き直したりするコマンドは？", "`git commit --amend`"),
    ("直前のコミットを取り消すが、作業した変更内容はステージングエリアに残すコマンドは？", "`git reset --soft HEAD~1`"),
    ("直前のコミットと、そこに含まれる作業内容を完全に破棄して元に戻すコマンドは？", "`git reset --hard HEAD~1`"),
    ("過去の特定のコミットで行われた変更を「打ち消す」ための新しいコミットを作成するコマンドは？", "`git revert <コミットID>`"),
    ("登録されているリモートリポジトリのURL一覧を表示するコマンドは？", "`git remote -v`"),
    ("新しいリモートリポジトリを `origin` という名前で登録するコマンドは？", "`git remote add origin <URL>`"),
    ("リモートリポジトリの最新情報を取得するが、自分のローカルファイルにはまだ統合させないコマンドは？", "`git fetch`"),
    ("ローカルのブランチを初めてリモートにプッシュし、upstream（追跡ブランチ）を設定するコマンドは？", "`git push -u origin <ブランチ名>`"),
    ("まだコミットしたくない中途半端な変更を、一時的に退避させるコマンドは？", "`git stash`"),
    ("退避させた作業（スタッシュ）の一覧を表示するコマンドは？", "`git stash list`"),
    ("最後に退避させた作業を復元し、退避リストから削除するコマンドは？", "`git stash pop`（スタッシュから削除されます）"),
    ("【よくある間違い】大容量ファイルやパスワードを含むファイルを誤ってコミットした場合、単純に rm で削除してコミットすれば履歴からも完全に消えるか？", "消えません。履歴から完全に消すには `git filter-repo` などの専用ツールによる歴史の書き換えが必要です"),
    ("【よくある間違い】`git push` で \"rejected (non-fast-forward)\" エラーが出た場合の主な原因と対処法は？", "原因: リモートに自分のローカルにない新しいコミットがある。対処法: `git pull`（または `git pull --rebase`）でリモートの変更を取り込んでから、再度 `git push` する"),
]

# Image filenames — each index matches cards[index] (50 items)
image_files = [
    "git-001-init.png",                 # 0  git init
    "git-002-clone.png",                # 1  git clone
    "git-003-status.png",               # 2  git status
    "git-004-add.png",                  # 3  git add
    "git-005-commit.png",               # 4  git commit
    "git-006-pull.png",                 # 5  git pull
    "git-007-push.png",                 # 6  git push
    "git-008-config-user.png",          # 7  user.name + user.email
    "git-009-config-name.png",          # 8  git config user.name
    "git-010-config-email.png",         # 9  git config user.email
    "git-011-gitconfig.png",            # 10 ~/.gitconfig
    "git-012-tag.png",                  # 11 git tag
    "git-013-worktree.png",             # 12 git worktree
    "git-014-worktree-add.png",         # 13 worktree add
    "git-015-worktree-safe.png",        # 14 safe worktree location
    "git-016-worktree-list.png",        # 15 worktree list
    "git-017-gitignore-worktree.png",   # 16 gitignore in worktree
    "git-018-worktree-remove.png",      # 17 worktree remove
    "git-019-worktree-blocked.png",     # 18 uncommitted changes block remove
    "git-020-worktree-force.png",       # 19 --force
    "git-021-worktree-prune.png",       # 20 worktree prune
    "git-022-worktree-branch-block.png",# 21 branch delete blocked by worktree
    "git-023-worktree-one-branch.png",  # 22 one branch per worktree rule
    "git-023-diff.png",                 # 23 git diff
    "git-024-diff-staged.png",          # 24 git diff --staged
    "git-025-log.png",                  # 25 git log
    "git-026-log-oneline.png",          # 26 git log --oneline
    "git-027-show.png",                 # 27 git show
    "git-028-branch-list.png",          # 28 git branch
    "git-029-branch-create.png",        # 29 git branch <name>
    "git-030-checkout.png",             # 30 git checkout / switch
    "git-031-checkout-b.png",           # 31 git checkout -b
    "git-032-merge.png",                # 32 git merge
    "git-033-branch-d.png",             # 33 git branch -d
    "git-034-branch-D.png",             # 34 git branch -D
    "git-035-restore.png",              # 35 git restore (working tree)
    "git-036-restore-staged.png",       # 36 git restore --staged
    "git-037-commit-amend.png",         # 37 git commit --amend
    "git-038-reset-soft.png",           # 38 git reset --soft
    "git-039-reset-hard.png",           # 39 git reset --hard
    "git-040-revert.png",               # 40 git revert
    "git-041-remote-v.png",             # 41 git remote -v
    "git-042-remote-add.png",           # 42 git remote add
    "git-043-fetch.png",                # 43 git fetch
    "git-044-push-u.png",               # 44 git push -u
    "git-045-stash.png",                # 45 git stash
    "git-046-stash-list.png",           # 46 git stash list
    "git-047-stash-pop.png",            # 47 git stash pop
    "git-048-filter-repo.png",          # 48 filter-repo mistake
    "git-049-non-fast-forward.png",     # 49 non-fast-forward error
]


def main():
    output_file = "git_deck.csv"

    # Combine into rows
    rows = []
    for (front, back), img in zip(cards, image_files):
        rows.append([front, back, img])

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["表面", "裏面", "Image"])
        writer.writerows(rows)

    print(f"✅ git_deck.csv を更新しました（{len(rows)} 問 + Image列）")
    print(f"   - スタイル参照: assets/images/simple-icon-set.jpg （24色限定フラットアイコン）")
    print(f"   - 画像フォルダ: assets/images/git-deck/")
    print(f"   - 現在生成済み画像: 実際のファイル数を確認してください")

if __name__ == "__main__":
    main()
