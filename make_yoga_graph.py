#!/bin/env python3
# -*- coding: utf-8 -*-

###################################################################
# Author: Eric Bullen
# Date: 4-June-2021
# Description:
#
# This tool provides a way to present yoga asanas that work well
# togehter constrained by requirements set by the user in strength
# and mobility, and outputs the map as a GraphViz Dot file.
###################################################################

import locale
import logging
import os
import shlex
import subprocess
import yaml
from collections import defaultdict

locale.setlocale(locale.LC_ALL, 'en_US')

# Log to the screen
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s: "%(name)s" (line: %(lineno)d) - %(levelname)s %(message)s'))

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Yoga(object):
    def __init__(self, yoga_data_file):
        self.graph = defaultdict(set)
        self.poses = self.load_data(yoga_data_file)


    def load_data(self, yoga_data_file):
        pose_data = dict()

        with open(yoga_data_file, "r") as fh:
            pose_data = yaml.load(fh, Loader=yaml.FullLoader)

        return pose_data


    def get_poses(self, intensity_levels=None, experience_levels=None, imp_strength_areas=None, imp_mobility_areas=None):
        all_poses = set(self.poses.keys())

        base = set()
        base.add("Your Choice")

        if intensity_levels:
            int_level_poses = set([pose for pose in self.poses if set([self.poses[pose]["intensity_level"]]) & set(intensity_levels)])
        else:
            int_level_poses = all_poses

        if experience_levels:
            exp_level_poses = set([pose for pose in self.poses if set([self.poses[pose]["experience_level"]]) & set(experience_levels)])
        else:
            exp_level_poses = all_poses

        if imp_strength_areas:
            imp_str_poses = set([pose for pose in self.poses if set(self.poses[pose]["improved_strength_sites"]) & set(imp_strength_areas)])
        else:
            imp_str_poses = all_poses

        if imp_mobility_areas:
            imp_mob_poses = set([pose for pose in self.poses if set(self.poses[pose]["improved_mobility_sites"]) & set(imp_mobility_areas)])
        else:
            imp_mob_poses = all_poses

        return base | (int_level_poses & exp_level_poses & imp_mob_poses & imp_str_poses)


    def get_info(self, pose):
        pulled_pose = self.poses.get(pose, {})

        intensity = pulled_pose.get("intensity_level", "n/a")
        experience = pulled_pose.get("experience_level", "n/a")
        imp_str_poses = pulled_pose.get("improved_strength_sites", ["n/a"])
        imp_mob_poses = pulled_pose.get("improved_mobility_sites", ["n/a"])

        return intensity, experience, imp_str_poses, imp_mob_poses


    def get_prep_poses(self, poses, limit_to_poses):
        all_prep_poses = set()

        for to_pose in poses:
            prep_poses = set(self.poses.get(to_pose, {}).get("prep_poses", ["Your Choice"]))
            prep_poses &= limit_to_poses

            all_prep_poses |= prep_poses

        return all_prep_poses


    def build_pose_tree(self, poses, limit_to_poses):
        if not self.graph:
            for pose in self.poses:
                for prep_pose in self.get_prep_poses([pose], limit_to_poses):
                    self.graph[prep_pose].add(pose)

        return self.graph


    def get_end_poses(self, pose_tree):
        all_to_poses = set()
        all_prep_poses = set()

        for prep_pose, to_poses in pose_tree.items():
            all_to_poses |= to_poses
            all_prep_poses.add(prep_pose)

        return all_to_poses - all_prep_poses


    def find_all_paths(self, pose_tree, start_pose, end_pose, min_chain_len, path = []):
        paths = list()
        path = path + [start_pose]

        if start_pose == end_pose:
            return [path]

        if start_pose != "Your Choice":
            if start_pose not in pose_tree:
                return []

        for pose in pose_tree.get(start_pose, "Your Choice"):
            if pose not in path:
                newpaths = self.find_all_paths(pose_tree, pose, end_pose, min_chain_len, path)

                for newpath in newpaths:
                    if len(newpath) >= min_chain_len:
                        paths.append(newpath)

        return paths


    def build_map(self, poses, limit_to_poses, min_chain_len):
        seen_poses = set()
        pose_map = dict()
        start_pose = "Your Choice"

        pose_tree = yoga.build_pose_tree(poses=interested_poses, limit_to_poses=interested_poses)
        end_poses = self.get_end_poses(pose_tree)

        for end_pose in end_poses:
            paths = self.find_all_paths(pose_tree, start_pose, end_pose, min_chain_len)

            if paths:
                logger.info("Found {path_len} paths from '{start}' to '{end}'".format(path_len=len(paths), start=start_pose, end=end_pose))
                pose_map[end_pose] = paths

                for path in paths:
                    seen_poses |= set(path)
            else:
                logger.info("Couldn't find any paths from '{start}' to '{end}'".format(start=start_pose, end=end_pose))

        return pose_map, seen_poses


    def clean(self, text):
        return text.replace("-", "_").replace(" ", "_").replace("/", "_").replace("'", "_")


    def make_graph(self, interested_poses, limit_to_poses, min_chain_len):
        pose_graph = list()

        contents = """
        digraph YogaPos {
            graph [label="Yoga Position Dependency Graph" labelloc=top fontsize=20 fontname="Verdana" concentrate=true];

            compound=true;
            rankdir=DU;

            //
            // Defaults
            //
            node [shape=record fontsize=10 fontname="Verdana" margin=0];

        REPLACE
        }
        """

        yoga_map, seen_poses = yoga.build_map(poses=interested_poses, limit_to_poses=limit_to_poses, min_chain_len=min_chain_len)

        for pose in seen_poses:
            pose_id = self.clean(pose)

            intensity, difficulty, imp_str_poses, imp_mob_poses = yoga.get_info(pose)

            if pose in interested_poses:
                pose_graph.append("{pose_id} [color=green label=\"{{{name}|Int: {int_level}|Exp: {exp_level}|Mob: {mobility}|Str: {strength}}}\"];".format(mobility=", ".join(imp_mob_poses), strength=", ".join(imp_str_poses), name=pose, int_level=intensity, exp_level=difficulty, pose_id=self.clean(pose_id)))
            else:
                pose_graph.append("{pose_id} [label=\"{{{name}|{int_level}|{exp_level}|Mob: {mobility}|Str: {strength}}}\"];".format(mobility=", ".join(imp_mob_poses), strength=", ".join(imp_str_poses), name=pose, int_level=intensity, exp_level=difficulty, pose_id=self.clean(pose_id)))

        pose_graph.append("")
        pose_graph.append("")

        # Find the longest first
        max_len = 0
        for paths in yoga_map.values():
            for path in paths:
                if len(path) > max_len:
                    max_len = len(path)

        pose_chains = list()
        for paths in yoga_map.values():
            for path in paths:
                pose_chain = " -> ".join([self.clean(pose) for pose in path])

                if len(path) == max_len:
                    pose_chain += " [color=green]"

                pose_chains.append("{pose_chain};".format(pose_chain=pose_chain))

        # Sorts chains by length so that edge colors are kept
        pose_chains = sorted(pose_chains, key=lambda chain: len(chain))
        pose_chains.reverse()
        pose_graph.extend(pose_chains)

        contents = contents.replace("REPLACE", "\n".join(pose_graph)).strip()

        return contents

    def get_available_options(self, record_type):
        options = set()

        for pose in self.poses.values():
            val = pose.get(record_type)

            if isinstance(val, list):
                options |= set(val)
            else:
                options.add(val)

        return options


###################################################################
if __name__ == "__main__":
    yoga = Yoga("yoga_asanas.yaml")

    experience_levels = yoga.get_available_options("experience_level")
    intensity_levels = yoga.get_available_options("intensity_level")
    mobility_areas = yoga.get_available_options("improved_mobility_sites") ^ set(["n/a"])
    strength_areas = yoga.get_available_options("improved_strength_sites") ^ set(["n/a"])

    if "EXPERIENCE_LEVELS" in os.environ:
        experience_levels = os.environ.get("EXPERIENCE_LEVELS").split(",")
    else:
        logger.warning("The 'EXPERIENCE_LEVELS' env var is not set. Using: '{levels}'.".format(levels=",".join(experience_levels)))

    if "INTENSITY_LEVELS" in os.environ:
        intensity_levels = os.environ.get("INTENSITY_LEVELS").split(",")
    else:
        logger.warning("The 'INTENSITY_LEVELS' env var is not set. Using: '{levels}'.".format(levels=",".join(intensity_levels)))

    if "MOBILITY_AREAS" in os.environ:
        mobility_areas = os.environ.get("MOBILITY_AREAS").split(",")
    else:
        logger.warning("The 'MOBILITY_AREAS' env var is not set. Using: '{areas}'.".format(areas=",".join(mobility_areas)))

    if "STRENGTH_AREAS" in os.environ:
        strength_areas = os.environ.get("STRENGTH_AREAS").split(",")
    else:
        logger.warning("The 'STRENGTH_AREAS' env var is not set. Using: '{areas}'.".format(areas=",".join(strength_areas)))

    if "MIN_CHAIN_LEN" not in os.environ:
        logger.warning("The 'MIN_CHAIN_LEN' env var for the minimum pose chain length is not set. Using: 8")

    min_chain_len = os.environ.get("MIN_CHAIN_LEN", 3)

    # Validation - Eric uses this as the graph is easy to verify.
    #intensity_levels = ["Low"]
    #experience_levels = ["Beginner"]
    #strength_areas = ["Back", "Abdomen"]
    #mobility_areas = ["Back", "Abdomen"]
    #min_chain_len = 8

    wanted_str_poses = yoga.get_poses(intensity_levels=intensity_levels, experience_levels=experience_levels, imp_strength_areas=strength_areas)
    wanted_mob_poses = yoga.get_poses(intensity_levels=intensity_levels, experience_levels=experience_levels, imp_mobility_areas=mobility_areas)

    interested_poses = wanted_str_poses | wanted_mob_poses

    graph = yoga.make_graph(interested_poses=interested_poses, limit_to_poses=interested_poses, min_chain_len=min_chain_len)

    with open("/data/yoga_graph.dot", "w") as fh:
        fh.write(graph)

    subprocess.run(shlex.split("dot -Tpng /data/yoga_graph.dot -o /data/yoga_graph.png"))
