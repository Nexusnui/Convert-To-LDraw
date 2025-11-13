from trimesh.transformations import is_same_transform, identity_matrix


def is_identity_matrix(matrix) -> bool:
    if matrix is None:
        return True
    return is_same_transform(identity_matrix(), matrix)