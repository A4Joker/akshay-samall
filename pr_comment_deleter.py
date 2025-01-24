#!/usr/bin/env python3

import sys
import re
import requests
from urllib.parse import urlparse
import argparse

class CommentDeleter:
    def __init__(self, token, pr_url):
        self.token = token
        self.pr_url = pr_url
        self.parse_url()
        
    def parse_url(self):
        """Parse the PR URL to determine the provider and extract relevant information."""
        parsed = urlparse(self.pr_url)
        self.domain = parsed.netloc
        path_parts = parsed.path.strip('/').split('/')
        
        if self.domain == 'github.bito.ai':
            self.provider = 'github-enterprise'
            self.api_base = f'https://{self.domain}/api/v3'
            if len(path_parts) >= 4:
                self.owner = path_parts[0]
                self.repo = path_parts[1]
                if path_parts[2] == 'pull':
                    self.pr_number = path_parts[3]
        elif 'bitbucket' in self.domain:
            self.provider = 'bitbucket'
            self.api_base = 'https://api.bitbucket.org/2.0'
            if len(path_parts) >= 4:
                self.workspace = path_parts[0]
                self.repo = path_parts[1]
                self.pr_number = path_parts[3]
        else:
            raise ValueError("Unsupported URL format or provider")

    def get_headers(self):
        """Get appropriate headers based on the provider."""
        if self.provider == 'github-enterprise':
            return {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
        elif self.provider == 'bitbucket':
            return {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

    def delete_github_enterprise_comments(self):
        """Delete all comments from a GitHub Enterprise PR."""
        # Delete issue comments
        comments_url = f'{self.api_base}/repos/{self.owner}/{self.repo}/issues/{self.pr_number}/comments'
        response = requests.get(comments_url, headers=self.get_headers())
        if response.status_code == 200:
            comments = response.json()
            for comment in comments:
                comment_id = comment['id']
                delete_url = f'{self.api_base}/repos/{self.owner}/{self.repo}/issues/comments/{comment_id}'
                delete_response = requests.delete(delete_url, headers=self.get_headers())
                print(f"Deleting comment {comment_id}: {'Success' if delete_response.status_code == 204 else 'Failed'}")

        # Delete review comments
        review_comments_url = f'{self.api_base}/repos/{self.owner}/{self.repo}/pulls/{self.pr_number}/comments'
        response = requests.get(review_comments_url, headers=self.get_headers())
        if response.status_code == 200:
            review_comments = response.json()
            for comment in review_comments:
                comment_id = comment['id']
                delete_url = f'{self.api_base}/repos/{self.owner}/{self.repo}/pulls/comments/{comment_id}'
                delete_response = requests.delete(delete_url, headers=self.get_headers())
                print(f"Deleting review comment {comment_id}: {'Success' if delete_response.status_code == 204 else 'Failed'}")

        # Clear PR description
        pr_url = f'{self.api_base}/repos/{self.owner}/{self.repo}/pulls/{self.pr_number}'
        update_response = requests.patch(pr_url, headers=self.get_headers(), json={'body': ''})
        print(f"Clearing PR description: {'Success' if update_response.status_code == 200 else 'Failed'}")

    def delete_bitbucket_comments(self):
        """Delete all comments from a Bitbucket PR."""
        # Get and delete PR comments
        comments_url = f'{self.api_base}/repositories/{self.workspace}/{self.repo}/pullrequests/{self.pr_number}/comments'
        response = requests.get(comments_url, headers=self.get_headers())
        if response.status_code == 200:
            comments = response.json()['values']
            for comment in comments:
                comment_id = comment['id']
                delete_url = f'{comments_url}/{comment_id}'
                delete_response = requests.delete(delete_url, headers=self.get_headers())
                print(f"Deleting comment {comment_id}: {'Success' if delete_response.status_code == 204 else 'Failed'}")

        # Clear PR description
        pr_url = f'{self.api_base}/repositories/{self.workspace}/{self.repo}/pullrequests/{self.pr_number}'
        update_response = requests.put(pr_url, headers=self.get_headers(), json={'description': ''})
        print(f"Clearing PR description: {'Success' if update_response.status_code == 200 else 'Failed'}")

    def delete_comments(self):
        """Delete all comments based on the provider."""
        try:
            if self.provider == 'github-enterprise':
                self.delete_github_enterprise_comments()
            elif self.provider == 'bitbucket':
                self.delete_bitbucket_comments()
            print("✨ Comment deletion completed!")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Delete all comments from a PR')
    parser.add_argument('token', help='Authentication token')
    parser.add_argument('pr_url', help='URL of the pull request')
    args = parser.parse_args()

    try:
        deleter = CommentDeleter(args.token, args.pr_url)
        deleter.delete_comments()
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()